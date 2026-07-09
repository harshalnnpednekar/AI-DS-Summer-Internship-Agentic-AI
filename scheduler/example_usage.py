import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

from scheduler import SchedulerManager, EventFetcher
from agent import NotificationWorkflow

load_dotenv()


def example_manual_event_processing():
    print("=== Manual Event Processing ===\n")
    
    workflow = NotificationWorkflow()
    
    sample_event = {
        "event_id": "evt-001",
        "title": "AI Workshop",
        "description": "Introduction to Agentic AI",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "department": "AIDS",
        "audience": "dept_only"
    }
    
    sample_students = [
        {"name": "Alice", "email": "alice@college.edu", "department": "AIDS"},
        {"name": "Bob", "email": "bob@college.edu", "department": "AIDS"}
    ]
    
    result = workflow.process_event(sample_event, sample_students)
    
    print(f"Event: {sample_event['title']}")
    print(f"Status: {result['status']}")
    print(f"Recipients: {len(sample_students)}")
    if result.get('notification_message'):
        print(f"\nGenerated Message:\n{result['notification_message']}")
    print()


def example_with_live_api():
    print("=== Live API Event Processing ===\n")
    
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    print(f"Using API URL: {api_url}\n")
    
    fetcher = EventFetcher(api_url)
    workflow = NotificationWorkflow()
    
    events = fetcher.fetch_upcoming_events(days=3)
    print(f"Found {len(events)} upcoming events\n")
    
    for event in events[:2]:
        print(f"Processing: {event['title']}")
        students = fetcher.get_students_for_event(event)
        print(f"  - Found {len(students)} students")
        
        result = workflow.process_event(event, students)
        print(f"  - Status: {result['status']}")
        print()


def example_scheduler_setup():
    print("=== Scheduler Setup ===\n")
    
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    scheduler = SchedulerManager(api_url)
    
    call_count = [0]
    
    def notification_callback(event, students):
        call_count[0] += 1
        print(f"[Callback #{call_count[0]}] Event: {event['title']}, Students: {len(students)}")
    
    scheduler.register_notification_callback(notification_callback)
    
    print("Scheduler configured with callback")
    print("Starting scheduler...")
    scheduler.start()
    
    print("\nScheduler jobs:")
    for job_info in scheduler.get_job_status():
        print(f"  - {job_info['name']}: {job_info['trigger']}")
    
    print("\nScheduler is running (runs check every 5 minutes)")
    print("Press Ctrl+C to stop\n")
    
    try:
        import time
        for i in range(3):
            time.sleep(10)
            print(f"Running... ({(i+1)*10}s elapsed)")
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Stopped")


def example_batch_processing():
    print("=== Batch Event Processing ===\n")
    
    workflow = NotificationWorkflow()
    
    events = [
        {
            "event_id": f"evt-{i:03d}",
            "title": f"Event {i}",
            "description": f"Description for event {i}",
            "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
            "department": "AIDS",
            "audience": "dept_only"
        }
        for i in range(1, 4)
    ]
    
    students_map = {
        "evt-001": [
            {"name": "Alice", "email": "alice@college.edu"},
            {"name": "Bob", "email": "bob@college.edu"}
        ],
        "evt-002": [
            {"name": "Charlie", "email": "charlie@college.edu"}
        ],
        "evt-003": [
            {"name": "David", "email": "david@college.edu"},
            {"name": "Eve", "email": "eve@college.edu"},
            {"name": "Frank", "email": "frank@college.edu"}
        ]
    }
    
    results = workflow.batch_process_events(events, students_map)
    
    print(f"Processed {len(results)} events\n")
    for i, result in enumerate(results, 1):
        print(f"Event {i}: {result['status']}")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <example>\n")
        print("Available examples:")
        print("  1. manual    - Manual event processing")
        print("  2. api       - Process events from live API")
        print("  3. scheduler - Setup and run scheduler")
        print("  4. batch     - Batch process multiple events")
        print()
        sys.exit(1)
    
    example = sys.argv[1].lower()
    
    if example == "manual" or example == "1":
        example_manual_event_processing()
    elif example == "api" or example == "2":
        example_with_live_api()
    elif example == "scheduler" or example == "3":
        example_scheduler_setup()
    elif example == "batch" or example == "4":
        example_batch_processing()
    else:
        print(f"Unknown example: {example}")
        sys.exit(1)
