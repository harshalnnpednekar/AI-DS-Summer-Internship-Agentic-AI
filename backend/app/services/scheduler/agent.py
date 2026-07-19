import logging
from typing import TypedDict, List, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.database import SessionLocal
from app.services.email.send_email import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationState(TypedDict):
    event: Dict[str, Any]
    users: List[Dict[str, Any]]
    notification_message: str
    status: str
    error: str
    notification_data: Dict[str, Any]

class NotificationAgent:
    def generate_notification_message(self, state: NotificationState) -> NotificationState:
        event = state["event"]
        
        try:
            subject = f"Reminder: {event.get('title')}"
            body = f"Hello,\\n\\nThis is a reminder for the upcoming event:\\n\\nTitle: {event.get('title')}\\nDate: {event.get('date')}\\nDepartment: {event.get('department')}\\n\\nDescription: {event.get('description')}\\n\\nPlease make sure to attend.\\n\\nBest regards,\\nEduAgent Notification System"
            
            response_text = f"SUBJECT: {subject}\\nBODY: {body}"
            
            state["notification_message"] = response_text
            state["status"] = "message_generated"
            return state
        except Exception as e:
            logger.error(f"Failed to generate message: {e}")
            state["error"] = str(e)
            state["status"] = "failed"
            return state

    def validate_event_data(self, state: NotificationState) -> NotificationState:
        event = state["event"]
        users = state["users"]
        
        if not event or not event.get("event_id"):
            state["error"] = "Invalid event data"
            state["status"] = "validation_failed"
            return state
        
        if not users or len(users) == 0:
            state["error"] = "No users found for event"
            state["status"] = "validation_failed"
            return state
        
        state["status"] = "validated"
        return state

    def prepare_notification_payload(self, state: NotificationState) -> NotificationState:
        event = state["event"]
        users = state["users"]
        
        payload = {
            "event_id": event.get("event_id"),
            "event_title": event.get("title"),
            "event_date": event.get("date"),
            "notification_message": state.get("notification_message", ""),
        }
        
        state["notification_data"] = payload
        state["status"] = "payload_prepared"
        return state

    def log_notification_attempt(self, state: NotificationState) -> NotificationState:
        if state.get("status") == "send_failed":
            logger.error(f"Failed to send notification for event {state['event'].get('event_id')}: {state.get('error')}")
            return state
            
        logger.info(f"Notification processing completed for event: {state['event'].get('event_id')}")
        logger.info(f"Attempted to notify {len(state['users'])} users")
        state["status"] = "logged"
        return state
    
    async def send_notification(self, state: NotificationState) -> NotificationState:
        event = state["event"]
        users = state["users"]
        try:
            async with SessionLocal() as db:
                for user in users:
                    await send_email(event, user, db)
            state["status"] = "sent"
        except Exception as e:
            logger.error(f"send_notification exception: {e}")
            state["error"] = str(e)
            state["status"] = "send_failed"
        return state


class NotificationWorkflow:
    def __init__(self):
        self.agent = NotificationAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(NotificationState)
        
        workflow.add_node("validate", self.agent.validate_event_data)
        workflow.add_node("generate_message", self.agent.generate_notification_message)
        workflow.add_node("prepare_payload", self.agent.prepare_notification_payload)
        workflow.add_node("send_notification", self.agent.send_notification)
        workflow.add_node("log_attempt", self.agent.log_notification_attempt)
        
        workflow.set_entry_point("validate")
        
        workflow.add_edge("validate", "generate_message")
        workflow.add_edge("generate_message", "prepare_payload")
        workflow.add_edge("prepare_payload", "send_notification")
        workflow.add_edge("send_notification", "log_attempt")
        workflow.add_edge("log_attempt", END)
        
        return workflow.compile()

    async def process_event(self, event: Dict[str, Any], users: List[Dict[str, Any]]) -> Dict[str, Any]:
        initial_state = NotificationState(  # type: ignore
            event=event,
            users=users,
            notification_message="",
            status="initialized",
            error=""
        )
        
        # We must use ainvoke for async graph execution
        result = await self.graph.ainvoke(initial_state)
        return result
