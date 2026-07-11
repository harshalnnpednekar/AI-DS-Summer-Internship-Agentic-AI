import os
import logging
import uuid
from .utils import extract_text_from_pdf
from .parser import parse_events
from .validator import AcademicEvent, EventList

logger = logging.getLogger(__name__)

def extract_events_from_pdf(pdf_path: str) -> list[dict]:
    try:
        text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        raise ValueError(f"Failed to read PDF: {e}")

    if not text.strip():
        logger.error("Extracted text is empty. No events to process.")
        raise ValueError("Extracted text is empty. No events to process.")

    raw_events = parse_events(text)
    
    valid_events = []
    for raw_event in raw_events:
        try:
            event = AcademicEvent(**raw_event)
            valid_events.append(event)
        except Exception as e:
            logger.error(f"Validation error for event '{raw_event.get('title', 'Unknown')}': {e}")

    return [event.model_dump() for event in valid_events]
