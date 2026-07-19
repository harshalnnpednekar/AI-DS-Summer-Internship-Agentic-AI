from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Event, StudentProfile, SendLog
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Events CRUD
async def get_event_by_id(db: AsyncSession, event_id: UUID) -> Event:
    result = await db.execute(select(Event).where(Event.event_id == event_id))
    return result.scalars().first()

async def get_upcoming_events(db: AsyncSession, days: int = 3) -> Sequence[Event]:
    now = datetime.now().date()
    end_date = now + timedelta(days=days)
    result = await db.execute(
        select(Event).where(Event.date >= now, Event.date <= end_date)
    )
    return result.scalars().all()

async def create_event(db: AsyncSession, event: Event):
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

async def update_event(db: AsyncSession, db_event: Event, update_data: dict):
    for key, value in update_data.items():
        setattr(db_event, key, value)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def delete_event(db: AsyncSession, event_id: UUID):
    event = await get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    await db.delete(event)
    await db.commit()

# Student Profiles CRUD
async def get_student_by_id(db: AsyncSession, student_id: UUID) -> Optional[StudentProfile]:
    result = await db.execute(select(StudentProfile).where(StudentProfile.id == student_id))
    return result.scalars().first()

async def get_students(db: AsyncSession, department: Optional[str] = None) -> Sequence[StudentProfile]:
    query = select(StudentProfile)
    result = await db.execute(query)
    return result.scalars().all()

async def create_student(db: AsyncSession, student: StudentProfile):
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student

async def update_student(db: AsyncSession, db_student: StudentProfile, update_data: dict):
    for key, value in update_data.items():
        setattr(db_student, key, value)
    await db.commit()
    await db.refresh(db_student)
    return db_student

async def delete_student(db: AsyncSession, student_id: UUID):
    student = await get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    await db.delete(student)
    await db.commit()

# Send Logs CRUD
async def create_send_log(db: AsyncSession, log: SendLog):
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log

async def get_send_log_by_event(db: AsyncSession, event_id: UUID) -> Sequence[SendLog]:
    result = await db.execute(
        select(SendLog).where(SendLog.event_id == event_id)
    )
    return result.scalars().all()