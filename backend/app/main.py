import sys
import asyncio

# Windows + Python 3.12+ uses ProactorEventLoop by default, which is
# incompatible with psycopg async. Force SelectorEventLoop on Windows.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import events, students, logs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EduAgent Event Notification API",
    description="Backend for college event notification system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(students.router)
app.include_router(logs.router)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "EduAgent API is running"}
