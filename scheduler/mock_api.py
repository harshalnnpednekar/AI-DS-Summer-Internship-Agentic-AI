import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Mock API for Scheduler Testing")


MOCK_EVENTS = [
    {
        "event_id": "evt-001",
        "title": "AI Workshop",
        "description": "Introduction to Agentic AI Systems",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "department": "AIDS",
        "audience": "dept_only"
    },
    {
        "event_id": "evt-002",
        "title": "General Assembly",
        "description": "Campus-wide general assembly",
        "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "department": "ALL",
        "audience": "all_students"
    },
    {
        "event_id": "evt-003",
        "title": "DS Hackathon",
        "description": "Data Science competition",
        "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "department": "ALL",
        "audience": "all_students"
    }
]

MOCK_STUDENTS = {
    "AIDS": [
        {
            "name": "Harshali",
            "email": "harshali@college.edu",
            "department": "AIDS"
        },
        {
            "name": "Priya",
            "email": "priya@college.edu",
            "department": "AIDS"
        }
    ],
    "ALL": [
        {
            "name": "Harshali",
            "email": "harshali@college.edu",
            "department": "AIDS"
        },
        {
            "name": "Priya",
            "email": "priya@college.edu",
            "department": "AIDS"
        },
        {
            "name": "John",
            "email": "john@college.edu",
            "department": "CSE"
        },
        {
            "name": "Sarah",
            "email": "sarah@college.edu",
            "department": "ECE"
        }
    ]
}

EMAIL_LOGS = []


@app.get("/events/upcoming")
async def get_upcoming_events(days: int = Query(3)):
    today = datetime.now().date()
    cutoff_date = today + timedelta(days=days)
    
    upcoming = []
    for event in MOCK_EVENTS:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        if today <= event_date <= cutoff_date:
            upcoming.append(event)
    
    return JSONResponse(content=upcoming)


@app.get("/students")
async def get_students(department: str = Query(...)):
    if department in MOCK_STUDENTS:
        return JSONResponse(content=MOCK_STUDENTS[department])
    return JSONResponse(content=[], status_code=404)


@app.post("/events")
async def create_events(events: List[Dict[str, Any]]):
    MOCK_EVENTS.extend(events)
    return JSONResponse(
        content={"message": f"Created {len(events)} events"},
        status_code=201
    )


@app.post("/send-log")
async def log_email(log_entry: Dict[str, Any]):
    EMAIL_LOGS.append(log_entry)
    return JSONResponse(
        content={"message": "Log recorded", "log_id": len(EMAIL_LOGS)},
        status_code=201
    )


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})


@app.get("/logs")
async def get_logs():
    return JSONResponse(content=EMAIL_LOGS)


if __name__ == "__main__":
    port = int(os.getenv("MOCK_API_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
