import re
import uuid
import logging
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

def standardize_date(date_str: str) -> str:
    if not date_str or date_str.strip() == "Unknown":
        raise ValueError("Empty or Unknown date string")
    try:
        dt = date_parser.parse(date_str, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        cleaned = re.split(r'\s*-\s*|\s+to\s+', date_str)[0].strip()
        if cleaned != date_str:
            try:
                dt = date_parser.parse(cleaned, fuzzy=True)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass
        raise ValueError(f"Could not parse date: '{date_str}'")

def determine_dept_and_audience(raw_dept: str, title: str, desc: str) -> tuple[str, str]:
    valid_depts = ["AIDS", "EXTC", "IT", "COMS", "ECS", "AURO", "MCA"]
    combined_text = f"{raw_dept} {title} {desc}".upper()
    found_dept = "ALL"
    for dept in valid_depts:
        if re.search(rf'\b{dept}\b', combined_text):
            found_dept = dept
            break
    audience = "all_students" if found_dept == "ALL" else "dept_only"
    return found_dept, audience

def parse_events(text: str) -> list[dict]:
    events = []
    lines = text.split('\n')
    event_pattern = re.compile(r'^(\d+)\s+(.+)$')
    date_pattern = re.compile(r'(\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+.*?|\*TBA)(?:\s*,|$)')

    generated_uuids = set()
    seen_events = set()
    
    def generate_unique_id():
        while True:
            new_id = str(uuid.uuid4())
            if new_id not in generated_uuids:
                generated_uuids.add(new_id)
                return new_id

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        raw_date, title, description, raw_dept = "", "", "Not specified", "Not specified"
        
        if '\t' in line:
            parts = [p.strip() for p in line.split('\t')]
            first_col_lower = parts[0].lower()
            if 'date' in first_col_lower or 'event' in first_col_lower or 'title' in first_col_lower or 'sr.no' in first_col_lower:
                continue
            
            if len(parts) >= 5:
                raw_date, title, description, raw_dept = parts[0], parts[1], parts[2] or "Not specified", parts[3] or "Not specified"
            elif len(parts) == 4:
                raw_date, title, description, raw_dept = parts[0], parts[1], parts[2] or "Not specified", parts[3] or "Not specified"
            elif len(parts) == 3:
                if any(char.isdigit() for char in parts[2]):
                    raw_date, title = parts[2], parts[1]
                else:
                    raw_date, title, description = parts[0], parts[1], parts[2] or "Not specified"
            elif len(parts) == 2:
                raw_date, title = parts[0], parts[1]
        else:
            match = event_pattern.match(line)
            if match:
                rest = match.group(2)
                date_match = date_pattern.search(rest)
                if date_match:
                    raw_date = date_match.group(1).strip()
                    title = rest[:date_match.start()].strip()
            else:
                continue

        if not raw_date or raw_date == "Unknown":
            logger.error(f"Missing date for event: '{title}'. Skipping.")
            continue
        if not title or title == "Unknown":
            logger.error(f"Missing title for event at date '{raw_date}'. Skipping.")
            continue
            
        try:
            formatted_date = standardize_date(raw_date)
        except ValueError as e:
            logger.error(f"Date conversion error: {e}. Skipping event: '{title}'")
            continue

        event_signature = (formatted_date, title.lower())
        if event_signature in seen_events:
            logger.warning(f"Duplicate event detected: '{title}' on {formatted_date}. Skipping.")
            continue
        seen_events.add(event_signature)

        department, audience = determine_dept_and_audience(raw_dept, title, description)

        events.append({
            "event_id": generate_unique_id(),
            "date": formatted_date,
            "title": title,
            "description": description,
            "department": department,
            "audience": audience
        })
                
    return events
