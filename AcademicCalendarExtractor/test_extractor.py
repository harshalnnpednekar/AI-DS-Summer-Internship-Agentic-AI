import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json
import uuid

from utils import extract_text_from_pdf
from parser import parse_events, standardize_date
from validator import AcademicEvent, EventList

class TestAcademicCalendarExtractor(unittest.TestCase):

    # --- 1. Date Conversion Tests ---
    def test_standardize_date_valid(self):
        self.assertEqual(standardize_date("12 July 2026"), "2026-07-12")
        self.assertEqual(standardize_date("12-Jul-26"), "2026-07-12")
        self.assertEqual(standardize_date("18th Aug - 22nd Aug 26"), "2026-08-18")

    def test_standardize_date_invalid(self):
        with self.assertRaises(ValueError):
            standardize_date("*TBA")
        with self.assertRaises(ValueError):
            standardize_date("Unknown")
        with self.assertRaises(ValueError):
            standardize_date("This is not a date")

    # --- 2. Event Extraction & UUID Generation Tests ---
    def test_parse_events(self):
        # Simulating a valid table row separated by tabs
        sample_text = "21st July 25\tBeginning of the Term\tOrientation\tIT\tAll Staff\n"
        events = parse_events(sample_text)
        
        self.assertEqual(len(events), 1)
        event = events[0]
        
        # Verify extraction logic mapped columns accurately
        self.assertEqual(event["date"], "2025-07-21")
        self.assertEqual(event["title"], "Beginning of the Term")
        self.assertEqual(event["department"], "IT")
        self.assertEqual(event["audience"], "dept_only")
        
        # Verify UUID4 Generation
        self.assertTrue("event_id" in event)
        # Will throw ValueError if not a valid UUID4
        parsed_uuid = uuid.UUID(event["event_id"], version=4)
        self.assertEqual(str(parsed_uuid), event["event_id"])

    # --- 3. JSON Validation (Pydantic) Tests ---
    def test_json_validation_valid(self):
        valid_data = {
            "event_id": str(uuid.uuid4()),
            "title": "Valid Event",
            "description": "Valid Description",
            "date": "2025-08-15",
            "department": "ALL",
            "audience": "all_students"
        }
        event = AcademicEvent(**valid_data)
        self.assertEqual(event.title, "Valid Event")

    def test_json_validation_invalid_date(self):
        invalid_data = {
            "event_id": str(uuid.uuid4()),
            "title": "Invalid Date",
            "description": "Desc",
            "date": "15-08-2025", # Not YYYY-MM-DD
            "department": "ALL",
            "audience": "all_students"
        }
        with self.assertRaises(ValueError):
            AcademicEvent(**invalid_data)

    def test_json_validation_invalid_uuid(self):
        invalid_data = {
            "event_id": "not-a-real-uuid",
            "title": "Invalid UUID",
            "description": "Desc",
            "date": "2025-08-15",
            "department": "ALL",
            "audience": "all_students"
        }
        with self.assertRaises(ValueError):
            AcademicEvent(**invalid_data)

    def test_json_validation_invalid_department(self):
        invalid_data = {
            "event_id": str(uuid.uuid4()),
            "title": "Invalid Dept",
            "description": "Desc",
            "date": "2025-08-15",
            "department": "INVALID_DEPT",
            "audience": "all_students"
        }
        with self.assertRaises(ValueError):
            AcademicEvent(**invalid_data)

    # --- 4. PDF Reading Tests ---
    @patch('utils.os.path.exists', return_value=True)
    @patch('utils.pdfplumber.open')
    def test_pdf_reading(self, mock_pdfplumber_open, mock_exists):
        # Mock pdfplumber context and page behavior
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Mocked PDF Text"
        mock_page.extract_tables.return_value = []
        mock_page.within_bbox.return_value = mock_page
        mock_pdf.pages = [mock_page]
        
        mock_pdfplumber_open.return_value.__enter__.return_value = mock_pdf
        
        text = extract_text_from_pdf("dummy.pdf")
        self.assertIn("Mocked PDF Text", text)

    # --- 5. JSON Export Tests ---
    def test_json_export(self):
        valid_data = {
            "event_id": str(uuid.uuid4()),
            "title": "Export Test",
            "description": "Export Desc",
            "date": "2026-01-01",
            "department": "IT",
            "audience": "dept_only"
        }
        event_list = EventList(events=[AcademicEvent(**valid_data)])
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_path = os.path.join(tmpdirname, "events.json")
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(event_list.model_dump_json(indent=4))
                
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIn("events", data)
                self.assertEqual(len(data["events"]), 1)
                self.assertEqual(data["events"][0]["title"], "Export Test")
                self.assertEqual(data["events"][0]["date"], "2026-01-01")

if __name__ == '__main__':
    unittest.main()
