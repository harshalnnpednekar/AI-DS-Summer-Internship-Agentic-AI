import sys
import asyncio

# Windows + Python 3.12+ uses ProactorEventLoop by default, which is
# incompatible with psycopg async. Force SelectorEventLoop on Windows.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import events, auth, attendance, users
import logging
from contextlib import asynccontextmanager

from app.services.scheduler.scheduler import SchedulerManager
from app.services.scheduler.agent import NotificationWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler_manager = SchedulerManager()
notification_workflow = NotificationWorkflow()

async def send_notification_callback(event, users):
    logger.info(f"Processing event: {event.get('title')}")
    result = await notification_workflow.process_event(event, users)
    
    if result.get("status") == "logged":
        logger.info(f"Notification prepared for {len(users)} users")
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
    title="EduAgent Event Notification API",
    description="Backend for college event notification system",
    version="1.0.0",
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

@app.get("/")
async def health_check():
    # Trigger reload
    return {"status": "ok", "message": "EduAgent API is running"}

