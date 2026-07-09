import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from config import config

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def render_template(event: dict, student: dict) -> str:
    template = jinja_env.get_template("event_notification.html")
    return template.render(
        event_title=event.get("title") or event.get("event_title", ""),
        student_name=student.get("name", "Student"),
        notification_message=event.get("notification_message", ""),
        event_date=event.get("date") or event.get("event_date", ""),
        department=event.get("department", "ALL"),
    )


def build_message(event: dict, student: dict) -> MIMEMultipart:
    subject = f"Reminder: {event.get('title') or event.get('event_title', 'Upcoming Event')}"
    html_body = render_template(event, student)

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{config.EMAIL_FROM_NAME} <{config.EMAIL_FROM}>"
    message["To"] = student.get("email")

    message.attach(MIMEText(html_body, "html"))
    return message


def send_email(event: dict, student: dict) -> bool:
    recipient = student.get("email")
    if not recipient:
        logger.error("Missing recipient email for student: %s", student)
        return False

    message = build_message(event, student)

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=15) as server:
            if config.SMTP_USE_TLS:
                server.starttls()
            if config.SMTP_USER and config.SMTP_PASSWORD:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.EMAIL_FROM, recipient, message.as_string())

        logger.info("Email sent successfully to %s", recipient)
        return True

    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient, str(e))
        return False
