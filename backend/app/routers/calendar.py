from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
import uuid
import logging
from datetime import datetime
from ..schemas_omnisync import StandardResponse
from ..services.calendar_extractor.extractor import extract_events_from_pdf
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Event
from ..dependencies import get_current_active_user, RoleChecker, RoleEnum

router = APIRouter(
    prefix="/api/calendar",
    tags=["Academic Calendar"],
)

logger = logging.getLogger(__name__)

allow_admin = RoleChecker([RoleEnum.HOD, RoleEnum.FACULTY])

@router.get("/events", response_model=StandardResponse)
async def get_all_events(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Event).order_by(Event.date))
        events = result.scalars().all()
        
        return StandardResponse(
            success=True,
            data={
                "events": [
                    {
                        "id": str(e.event_id),
                        "title": e.title,
                        "description": e.description,
                        "date": e.date.strftime("%b %d, %Y"),
                        "department": e.department,
                        "audience": e.audience
                    } for e in events
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        return StandardResponse(success=False, data=None, error=str(e))

@router.post("/extract", response_model=StandardResponse)
async def extract_calendar(
    file: UploadFile = File(...),
    current_user = Depends(allow_admin),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    temp_file_path = f"temp_{uuid.uuid4()}.pdf"
    try:
        content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)

        extracted_events = extract_events_from_pdf(temp_file_path)
        
        # We can either save them to the database or just return them. 
        # The prompt says "parses it and broadcasts deadline alerts automatically".
        # Let's save them to the DB.
        
        new_events_count = 0
        for event_data in extracted_events:
            # We skip duplicates in DB if we want, or just insert them.
            # Let's just insert them.
            new_event = Event(
                title=event_data["title"],
                description=event_data["description"],
                date=datetime.strptime(event_data["date"], "%Y-%m-%d").date(),
                department=event_data["department"],
                audience=event_data["audience"]
            )
            db.add(new_event)
            new_events_count += 1
            
        await db.commit()
        
        return StandardResponse(
            success=True,
            data={
                "message": f"Successfully extracted and saved {new_events_count} events.",
                "extracted_events": extracted_events
            }
        )

    except Exception as e:
        logger.error(f"Error during calendar extraction: {e}")
        return StandardResponse(
            success=False,
            data=None,
            error=str(e)
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
