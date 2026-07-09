import argparse
import os
import logging
from utils import extract_text_from_pdf
from parser import parse_events
from validator import AcademicEvent, EventList
import config

# Global logging configuration targeting both terminal and extractor.log
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("extractor.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    arg_parser = argparse.ArgumentParser(description="Extract academic events from a PDF calendar.")
    arg_parser.add_argument("--pdf", default="academic_calendar.pdf", help="Path to the academic calendar PDF")
    arg_parser.add_argument("--output", default=config.DEFAULT_OUTPUT_FILE, help="Path to save the extracted events")
    args = arg_parser.parse_args()

    try:
        logger.info(f"PDF loaded: {args.pdf}")
        text = extract_text_from_pdf(args.pdf)
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        return

    if not text.strip():
        logger.error("Extracted text is empty. No events to process.")
        return

    raw_events = parse_events(text)
    logger.info(f"Events extracted: Found {len(raw_events)} potential raw events.")
    
    valid_events = []
    for raw_event in raw_events:
        try:
            event = AcademicEvent(**raw_event)
            valid_events.append(event)
        except Exception as e:
            logger.error(f"Validation error for event '{raw_event.get('title', 'Unknown')}': {e}")

    event_list = EventList(events=valid_events)
    logger.info("Validation completed.")

    dir_name = os.path.dirname(args.output)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json_data = event_list.model_dump_json(indent=4)
        f.write(json_data)
        
    logger.info(f"JSON exported: {len(valid_events)} valid events securely written to {args.output}")

if __name__ == "__main__":
    main()
