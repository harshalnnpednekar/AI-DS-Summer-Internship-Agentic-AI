import logging
import httpx
from datetime import datetime, timezone
from config import config

logger = logging.getLogger(__name__)


def post_send_log(event_id: str, student_email: str, status: str) -> bool:
    payload = {
        "event_id": event_id,
        "student_email": student_email,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    url = f"{config.API_BASE_URL}/send-log"

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
        logger.info("Logged delivery status for %s: %s", student_email, status)
        return True

    except Exception as e:
        logger.error("Failed to log delivery status for %s: %s", student_email, str(e))
        return False
