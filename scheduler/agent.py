import os
import requests
from typing import TypedDict, List, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from groq import Groq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationState(TypedDict):
    event: Dict[str, Any]
    students: List[Dict[str, Any]]
    notification_message: str
    status: str
    error: str
    notification_data: Dict[str, Any]

class NotificationAgent:
    def __init__(self, api_key: str = None):
        self.client = Groq(
            api_key=api_key or os.getenv("GROQ_API_KEY")
        )
        self.model = "llama-3.1-8b-instant"
        # Email service URL for sending notifications
        self.email_service_url = os.getenv("EMAIL_SERVICE_URL", "http://localhost:8002")

    def generate_notification_message(self, state: NotificationState) -> NotificationState:
        event = state["event"]
        
        prompt = f"""
Generate a concise email subject and body for the following event:

Event Title: {event.get('title')}
Event Description: {event.get('description')}
Event Date: {event.get('date')}
Department: {event.get('department')}

The message should be professional, clear, and encouraging attendance.
Format the response as:
SUBJECT: [subject line]
BODY: [email body]
"""
        
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
            )
            
            response_text = message.choices[0].message.content
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
        students = state["students"]
        
        if not event or not event.get("event_id"):
            state["error"] = "Invalid event data"
            state["status"] = "validation_failed"
            return state
        
        if not students or len(students) == 0:
            state["error"] = "No students found for event"
            state["status"] = "validation_failed"
            return state
        
        state["status"] = "validated"
        return state

    def prepare_notification_payload(self, state: NotificationState) -> NotificationState:
        event = state["event"]
        students = state["students"]
        
        payload = {
            "event_id": event.get("event_id"),
            "event_title": event.get("title"),
            "event_date": event.get("date"),
            "students": [
                {
                    "name": s.get("name", "Student"),
                    "email": s.get("email"),
                    "department": s.get("department"),
                }
                for s in students
            ],
            "notification_message": state.get("notification_message", ""),
            "created_at": datetime.now().isoformat()
        }
        
        state["notification_data"] = payload
        state["status"] = "payload_prepared"
        return state

    def log_notification_attempt(self, state: NotificationState) -> NotificationState:
        if state.get("status") == "send_failed":
            logger.error(f"Failed to send notification for event {state['event'].get('event_id')}: {state.get('error')}")
            return state
            
        logger.info(f"Notification prepared for event: {state['event'].get('event_id')}")
        logger.info(f"Recipients: {len(state['students'])} students")
        state["status"] = "logged"
        return state
    
    def send_notification(self, state: NotificationState) -> NotificationState:
        
        payload = state.get("notification_data")
        try:
            logger.info(f"Sending payload to {self.email_service_url}/notify")
            response = requests.post(f"{self.email_service_url}/notify", json=payload, timeout=15)
            response.raise_for_status()
            state["status"] = "sent"
        except Exception as e:
            logger.error(f"send_notification exception: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            state["error"] = str(e)
            state["status"] = "send_failed"
        return state


class NotificationWorkflow:
    def __init__(self, api_key: str = None):
        self.agent = NotificationAgent(api_key)
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

    def process_event(self, event: Dict[str, Any], students: List[Dict[str, Any]]) -> Dict[str, Any]:
        initial_state = NotificationState(
            event=event,
            students=students,
            notification_message="",
            status="initialized",
            error=""
        )
        
        result = self.graph.invoke(initial_state)
        return result

    def batch_process_events(self, events: List[Dict[str, Any]], students_map: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        results = []
        for event in events:
            students = students_map.get(event.get("event_id"), [])
            result = self.process_event(event, students)
            results.append(result)
        return results
