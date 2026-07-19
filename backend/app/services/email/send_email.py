import smtplib
import logging
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, timezone

from app.config import settings
from app.models import SendLog
from app.crud import create_send_log

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

def render_template(event: dict, user: dict) -> str:
    template = jinja_env.get_template("event_notification.html")
    return template.render(
        event_title=event.get("title") or event.get("event_title", ""),
        student_name=user.get("name", "User"),
        notification_message=event.get("notification_message", ""),
        event_date=event.get("date") or event.get("event_date", ""),
        department=event.get("department", "ALL"),
    )

def build_message(event: dict, user: dict) -> MIMEMultipart:
    subject = f"Reminder: {event.get('title') or event.get('event_title', 'Upcoming Event')}"
    html_body = render_template(event, user)

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    message["To"] = user.get("email")  # type: ignore

    message.attach(MIMEText(html_body, "html"))
    return message

def _send_email_sync(recipient: str, message: MIMEMultipart) -> bool:
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15) as server:  # type: ignore
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, recipient, message.as_string())  # type: ignore
        logger.info("Email sent successfully to %s", recipient)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient, str(e))
        return False

async def send_email(event: dict, user: dict, db: AsyncSession) -> bool:
    recipient = user.get("email")
    if not recipient:
        logger.error("Missing recipient email for user: %s", user)
        return False

    message = build_message(event, user)
    
    # Run the synchronous SMTP call in a thread pool so it doesn't block FastAPI
    sent = await asyncio.to_thread(_send_email_sync, recipient, message)
    
    # Log to DB
    status = "sent" if sent else "failed"
    try:
        db_log = SendLog(
            event_id=uuid.UUID(event["event_id"]),
            student_email=recipient,
            status=status,
            timestamp=datetime.now(timezone.utc)
        )
        await create_send_log(db, db_log)
    except Exception as e:
        logger.error("Failed to write SendLog for %s: %s", recipient, str(e))
        
    return sent
