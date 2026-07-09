import logging
import time
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List, Optional

from config import config
from send_email import send_email
from log_client import post_send_log
from monitoring.metrics import (
    EMAILS_SENT_TOTAL,
    EMAIL_SEND_DURATION_SECONDS,
    NOTIFICATION_BATCH_SIZE,
    get_metrics,
)
from monitoring.sentry_setup import init_sentry

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

init_sentry()

app = FastAPI(title="Email Delivery Service")


class Student(BaseModel):
    name: Optional[str] = "Student"
    email: str
    department: Optional[str] = None


class NotificationPayload(BaseModel):
    event_id: str
    event_title: str
    event_date: str
    department: Optional[str] = "ALL"
    notification_message: str
    students: List[Student]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get(config.PROMETHEUS_METRICS_PATH)
def metrics():
    data, content_type = get_metrics()
    return Response(content=data, media_type=content_type)


@app.post("/notify")
def notify(payload: NotificationPayload):
    event = {
        "event_id": payload.event_id,
        "title": payload.event_title,
        "date": payload.event_date,
        "department": payload.department,
        "notification_message": payload.notification_message,
    }

    results = []
    NOTIFICATION_BATCH_SIZE.observe(len(payload.students))

    for student in payload.students:
        student_dict = student.model_dump()
        start = time.time()
        sent = send_email(event, student_dict)
        EMAIL_SEND_DURATION_SECONDS.observe(time.time() - start)

        status = "sent" if sent else "failed"
        EMAILS_SENT_TOTAL.labels(status=status).inc()

        post_send_log(payload.event_id, student.email, status)
        results.append({"email": student.email, "status": status})

    return {"event_id": payload.event_id, "results": results}
