from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import SendLogCreate, SendLogResponse
from app.models import SendLog
from app import crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-log", response_model=SendLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    payload: SendLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Store an email delivery log.
    """
    try:
        db_log = SendLog(**payload.model_dump())
        created = await crud.create_send_log(db, db_log)
        return created
    except Exception as e:
        logger.error(f"Error creating send log: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create send log: {str(e)}"
        )
