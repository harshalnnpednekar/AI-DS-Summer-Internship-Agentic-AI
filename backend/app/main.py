import sys
import asyncio
import selectors

# Windows + Python 3.12+ uses ProactorEventLoop by default, which is
# incompatible with psycopg async. Replace the running loop with a
# SelectorEventLoop before any DB connections are made.
if sys.platform == "win32":
    _selector = selectors.SelectSelector()
    _loop = asyncio.SelectorEventLoop(_selector)
    asyncio.set_event_loop(_loop)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import events, auth, attendance, users, subjects, certificates
import logging
from contextlib import asynccontextmanager

from app.services.scheduler.scheduler import SchedulerManager
from app.services.scheduler.agent import NotificationWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler_manager = SchedulerManager()
notification_workflow = NotificationWorkflow()

async def send_notification_callback(event, users_list):
    logger.info(f"Processing event: {event.get('title')}")
    result = await notification_workflow.process_event(event, users_list)
    
    if result.get("status") == "logged":
        logger.info(f"Notification prepared for {len(users_list)} users")
    else:
        logger.error(f"Failed to process event: {result.get('error')}")

scheduler_manager.register_notification_callback(send_notification_callback)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting background scheduler...")
    scheduler_manager.start()
    yield
    # Shutdown
    logger.info("Stopping background scheduler...")
    scheduler_manager.stop()

app = FastAPI(
    title="EduAgent API",
    description="Backend for the College Academic and Event Notification System",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(users.router)
app.include_router(subjects.router)
app.include_router(certificates.router)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "EduAgent API v2.0 is running"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
