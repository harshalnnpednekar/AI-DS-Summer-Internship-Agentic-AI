from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas import StudentResponse
from app import crud
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["students"])

@router.get("", response_model=List[StudentResponse])
async def read_students(
    department: str = "ALL",
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve students, optionally filtered by department.
    If department is 'ALL', returns all students.
    """
    try:
        students = await crud.get_students(db, department=department)
        return students
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve students."
        )
