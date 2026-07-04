from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from app.database import get_db
from app.schemas import EventCreate, EventResponse
from app.models import Event
from app import crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/upcoming", response_model=List[EventResponse])
async def read_upcoming_events(
    days: int = 2,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all upcoming events for the next N days (defaults to 2).
    """
    try:
        events = await crud.get_upcoming_events(db, days=days)
        return events
    except Exception as e:
        logger.error(f"Error fetching upcoming events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve upcoming events."
        )

@router.post("", response_model=Union[EventResponse, List[EventResponse]], status_code=status.HTTP_201_CREATED)
async def create_events(
    payload: Union[EventCreate, List[EventCreate]],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a single event or a bulk list of events.
    """
    try:
        if isinstance(payload, list):
            created_events = []
            for event_data in payload:
                db_event = Event(**event_data.model_dump())
                created = await crud.create_event(db, db_event)
                created_events.append(created)
            return created_events
        else:
            db_event = Event(**payload.model_dump())
            created = await crud.create_event(db, db_event)
            return created
    except Exception as e:
        logger.error(f"Error creating event(s): {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create event: {str(e)}"
        )
