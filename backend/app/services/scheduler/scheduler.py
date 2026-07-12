import os
from datetime import datetime
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.database import SessionLocal
from app.crud import get_upcoming_events
from app.models import User, StudentProfile, FacultyProfile
from sqlalchemy.future import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_users_by_department(db, department: str) -> List[Dict[str, Any]]:
    users_list = []
    
    # 1. Fetch Students
    student_query = select(User, StudentProfile).join(StudentProfile, User.id == StudentProfile.user_id)
    if department != "ALL":
        student_query = student_query.where(StudentProfile.department == department)
        
    student_results = await db.execute(student_query)
    for user, profile in student_results.all():
        users_list.append({
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "role": user.role.value,
            "department": profile.department
        })

    # 2. Fetch Faculty and HOD
    faculty_query = select(User, FacultyProfile).join(FacultyProfile, User.id == FacultyProfile.user_id)
    if department != "ALL":
        faculty_query = faculty_query.where(FacultyProfile.department == department)
        
    faculty_results = await db.execute(faculty_query)
    for user, profile in faculty_results.all():
        users_list.append({
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "role": user.role.value,
            "department": profile.department
        })
        
    return users_list


class NotificationChecker:
    def __init__(self, notification_days: int = 7):
        self.notification_days = notification_days

    def should_notify(self, event_date_str: str) -> bool:
        try:
            event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            days_until = (event_date - today).days
            return 0 <= days_until <= self.notification_days
        except ValueError:
            logger.error(f"Invalid date format: {event_date_str}")
            return False


class SchedulerManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.notification_checker = NotificationChecker()
        self.callbacks = []

    def register_notification_callback(self, callback):
        self.callbacks.append(callback)

    def trigger_callbacks(self, event: Dict[str, Any], users: List[Dict[str, Any]]):
        for callback in self.callbacks:
            try:
                callback(event, users)
            except Exception as e:
                logger.error(f"Callback failed: {e}")

    async def check_events(self):
        try:
            async with SessionLocal() as db:
                events = await get_upcoming_events(db, days=7)
                
                for event in events:
                    event_dict = {
                        "event_id": str(event.event_id),
                        "title": event.title,
                        "description": event.description,
                        "date": str(event.date),
                        "department": event.department,
                    }
                    if self.notification_checker.should_notify(event_dict["date"]):
                        users = await fetch_users_by_department(db, event_dict.get("department") or "ALL")
                        
                        if users:
                            self.trigger_callbacks(event_dict, users)
        except Exception as e:
            logger.error(f"Failed to check events: {e}")

    def start(self):
        if not self.scheduler.running:
            self.scheduler.add_job(
                self.check_events,
                trigger=CronTrigger(minute="*/5"),
                id="event_check_job",
                name="Check upcoming events",
                replace_existing=True
            )
            self.scheduler.start()
            logger.info("Scheduler started via AsyncIOScheduler")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def get_job_status(self):
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger)
            }
            for job in jobs
        ]
