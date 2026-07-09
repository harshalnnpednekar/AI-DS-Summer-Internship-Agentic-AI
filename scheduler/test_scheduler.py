import unittest
from datetime import datetime, timedelta
from scheduler import EventFetcher, NotificationChecker, SchedulerManager
from agent import NotificationWorkflow, NotificationAgent
import os


class TestNotificationChecker(unittest.TestCase):
    def setUp(self):
        self.checker = NotificationChecker(notification_days=3)

    def test_should_notify_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue(self.checker.should_notify(today))

    def test_should_notify_tomorrow(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertTrue(self.checker.should_notify(tomorrow))

    def test_should_notify_in_3_days(self):
        in_3_days = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        self.assertTrue(self.checker.should_notify(in_3_days))

    def test_should_not_notify_past(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertFalse(self.checker.should_notify(yesterday))

    def test_should_not_notify_beyond_window(self):
        far_future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        self.assertFalse(self.checker.should_notify(far_future))

    def test_invalid_date_format(self):
        self.assertFalse(self.checker.should_notify("invalid-date"))


class TestNotificationAgent(unittest.TestCase):
    def setUp(self):
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        self.agent = NotificationAgent()

    def test_validate_event_data_valid(self):
        state = {
            "event": {
                "event_id": "evt-001",
                "title": "Test Event",
                "description": "Test",
                "date": "2026-07-12"
            },
            "students": [
                {"name": "John", "email": "john@test.com"}
            ],
            "notification_message": "",
            "status": "initialized",
            "error": ""
        }
        result = self.agent.validate_event_data(state)
        self.assertEqual(result["status"], "validated")

    def test_validate_event_data_missing_event_id(self):
        state = {
            "event": {"title": "Test Event"},
            "students": [{"name": "John", "email": "john@test.com"}],
            "notification_message": "",
            "status": "initialized",
            "error": ""
        }
        result = self.agent.validate_event_data(state)
        self.assertEqual(result["status"], "validation_failed")

    def test_validate_event_data_no_students(self):
        state = {
            "event": {"event_id": "evt-001", "title": "Test Event"},
            "students": [],
            "notification_message": "",
            "status": "initialized",
            "error": ""
        }
        result = self.agent.validate_event_data(state)
        self.assertEqual(result["status"], "validation_failed")

    def test_prepare_notification_payload(self):
        state = {
            "event": {
                "event_id": "evt-001",
                "title": "Test Event",
                "date": "2026-07-12"
            },
            "students": [
                {"email": "john@test.com"},
                {"email": "jane@test.com"}
            ],
            "notification_message": "Test message",
            "status": "initialized",
            "error": ""
        }
        result = self.agent.prepare_notification_payload(state)
        self.assertEqual(result["status"], "payload_prepared")
        self.assertIn("notification_data", result)
        self.assertEqual(len(result["notification_data"]["student_emails"]), 2)


class TestSchedulerManager(unittest.TestCase):
    def setUp(self):
        self.manager = SchedulerManager()

    def test_callback_registration(self):
        callback_called = False

        def test_callback(event, students):
            nonlocal callback_called
            callback_called = True

        self.manager.register_notification_callback(test_callback)
        self.assertEqual(len(self.manager.callbacks), 1)

    def test_multiple_callbacks(self):
        def callback1(event, students):
            pass

        def callback2(event, students):
            pass

        self.manager.register_notification_callback(callback1)
        self.manager.register_notification_callback(callback2)
        self.assertEqual(len(self.manager.callbacks), 2)


class TestNotificationWorkflow(unittest.TestCase):
    def setUp(self):
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        self.workflow = NotificationWorkflow()

    def test_workflow_initialization(self):
        self.assertIsNotNone(self.workflow.graph)
        self.assertIsNotNone(self.workflow.agent)


if __name__ == "__main__":
    unittest.main()
