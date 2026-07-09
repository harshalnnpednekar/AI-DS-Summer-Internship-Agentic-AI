# Scheduler & Agent Module (Person 3)

Automatic event detection and notification triggering system using APScheduler and LangGraph.

## Overview

This module handles:
- Fetching upcoming events from the backend API
- Checking if events fall within the notification window
- Generating notification messages using Claude AI
- Preparing notification payloads for the email service

## Project Structure

```
scheduler/
├── scheduler.py         # APScheduler setup and event fetching
├── agent.py            # LangGraph workflow for notification generation
├── mock_api.py         # Mock API for testing
├── main.py             # Application entry point
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/harshalnnpednekar/AI-DS-Summer-Internship-Agentic-AI.git
cd scheduler
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your API key and configuration
```

## Usage

### Run with Mock API (for testing):

```bash
python mock_api.py
```

In another terminal:

```bash
python main.py run
```

### Run with Person 2's Backend:

Update `.env`:
```
API_BASE_URL=http://localhost:8000
MOCK_API_ENABLED=false
```

Then:
```bash
python main.py run
```

### Check Status:

```bash
python main.py status
```

## Configuration

Edit `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | http://localhost:8000 | Backend API URL |
| `SCHEDULER_INTERVAL_MINUTES` | 5 | How often to check events |
| `NOTIFICATION_WINDOW_DAYS` | 3 | Days before event to notify |
| `ANTHROPIC_API_KEY` | - | Claude API key (required) |
| `LOG_LEVEL` | INFO | Logging level |
| `MOCK_API_ENABLED` | true | Use mock API for testing |
| `MOCK_API_PORT` | 8001 | Port for mock API |

## Components

### EventFetcher
Fetches upcoming events and students from the API.

```python
fetcher = EventFetcher("http://localhost:8000")
events = fetcher.fetch_upcoming_events(days=3)
```

### NotificationChecker
Determines if an event should trigger a notification.

```python
checker = NotificationChecker(notification_days=3)
should_notify = checker.should_notify("2026-07-12")
```

### SchedulerManager
Manages APScheduler and triggers callbacks.

```python
manager = SchedulerManager()
manager.register_notification_callback(my_callback)
manager.start()
```

### NotificationAgent
Uses Claude AI to generate notification messages.

```python
agent = NotificationAgent()
state = agent.generate_notification_message(state)
```

### NotificationWorkflow
LangGraph workflow orchestrating the notification process.

```python
workflow = NotificationWorkflow()
result = workflow.process_event(event, students)
```

## Integration Points

1. **With Person 2's Backend**: Update `API_BASE_URL` in `.env`
2. **With Person 4's Email Service**: Use the callback system

```python
def email_callback(event, students):
    # Person 4 handles sending emails
    pass

manager.register_notification_callback(email_callback)
```

## API Contract (from Person 2)

### GET /events/upcoming?days=3
Returns list of events within the next N days.

### GET /students?department=X
Returns students in a specific department.

### POST /send-log
Logs email delivery attempts.

```json
{
  "event_id": "uuid",
  "student_email": "email@example.com",
  "status": "success",
  "timestamp": "2026-07-09T10:00:00Z"
}
```

## Testing

### Test with mock data:
```bash
python mock_api.py &
python main.py run
```

### Monitor logs:
```bash
tail -f scheduler.log
```

### Check job status:
```bash
python main.py status
```

## Architecture

```
┌─────────────────────────────────────────────┐
│       APScheduler (Every 5 minutes)         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │  EventFetcher       │
        │  (Fetch Events)     │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ NotificationChecker │
        │ (Check Window)      │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ NotificationWorkflow│
        │ (LangGraph)         │
        └────────┬────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
        ▼                  ▼
   Validate          Generate Message
        │                  │
        ▼                  ▼
   Prepare Payload    Log Attempt
        │                  │
        └────────┬─────────┘
                 │
                 ▼
         Callback Function
         (Email Service)
```

## Logging

All logs are output to console and stored in `scheduler.log`.

Log levels:
- INFO: Normal operations
- ERROR: Failures and exceptions
- DEBUG: Detailed debugging info

## Troubleshooting

### "Failed to fetch events"
- Check if Person 2's backend is running
- Verify API_BASE_URL in .env

### "Invalid date format"
- Ensure events have date in YYYY-MM-DD format

### "No students found"
- Verify students are created in Person 2's database
- Check department name matches

### "Anthropic API key not found"
- Add ANTHROPIC_API_KEY to .env

## Development Notes

- Scheduler runs in background (non-blocking)
- All errors are caught and logged
- Graceful shutdown with Ctrl+C
- Mock API for independent testing

## Next Steps

1. Deploy with Person 2's backend
2. Integrate with Person 4's email service
3. Add monitoring and alerting
4. Deploy to production environment
