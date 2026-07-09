import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventFetcher:
    def __init__(self, api_base_url: str = None):
        self.api_base_url = api_base_url or os.getenv(
            "API_BASE_URL", "http://localhost:8000"
        )

    def fetch_upcoming_events(self, days: int = 3) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.api_base_url}/events/upcoming",
                params={"days": days},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch events: {e}")
            return []

    def get_students_for_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            department = event.get("department")
            response = requests.get(
                f"{self.api_base_url}/students",
                params={"department": department},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch students: {e}")
            return []


class NotificationChecker:
    def __init__(self, notification_days: int = 3):
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
    def __init__(self, api_base_url: str = None):
        self.scheduler = BackgroundScheduler()
        self.event_fetcher = EventFetcher(api_base_url)
        self.notification_checker = NotificationChecker()
        self.callbacks = []

    def register_notification_callback(self, callback):
        self.callbacks.append(callback)

    def trigger_callbacks(self, event: Dict[str, Any], students: List[Dict[str, Any]]):
        for callback in self.callbacks:
            try:
                callback(event, students)
            except Exception as e:
                logger.error(f"Callback failed: {e}")

    def check_events(self):
        events = self.event_fetcher.fetch_upcoming_events()
        
        for event in events:
            if self.notification_checker.should_notify(event.get("date")):
                students = self.event_fetcher.get_students_for_event(event)
                
                if event.get("audience") == "all_students":
                    self.trigger_callbacks(event, students)
                elif event.get("audience") == "dept_only":
                    self.trigger_callbacks(event, students)

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
            logger.info("Scheduler started")

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
