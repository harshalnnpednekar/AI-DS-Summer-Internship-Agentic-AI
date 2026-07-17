from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models import Subject, FacultySubjectMapping, User
from app.schemas import SubjectResponse, SubjectBase, FacultySubjectMappingResponse
from app.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

@router.get("", response_model=List[SubjectResponse])
async def get_subjects(
    year: Optional[str] = None,
    semester: Optional[int] = None,
    department_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Subject)
    if year:
        query = query.where(Subject.year == year)
    if semester:
        query = query.where(Subject.semester == semester)
    if department_id:
        query = query.where(Subject.department_id == department_id)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=SubjectResponse)
async def create_subject(
    subject: SubjectBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["HOD", "FACULTY"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_subject = Subject(**subject.model_dump())
    db.add(new_subject)
    await db.commit()
    await db.refresh(new_subject)
    return new_subject

@router.get("/faculty", response_model=List[SubjectResponse])
async def get_faculty_subjects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["HOD", "FACULTY"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    query = select(Subject).join(FacultySubjectMapping, Subject.id == FacultySubjectMapping.subject_id)\
                           .where(FacultySubjectMapping.faculty_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/faculty/map/{subject_id}")
async def map_faculty_subject(
    subject_id: UUID,
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["HOD", "FACULTY"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Check if subject exists
    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    mapping = FacultySubjectMapping(
        faculty_id=current_user.id,
        class_id=class_id,
        subject_id=subject_id
    )
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return {"message": "Subject mapped successfully", "id": mapping.id}

@router.delete("/faculty/map/{subject_id}")
async def unmap_faculty_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["HOD", "FACULTY"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    query = select(FacultySubjectMapping).where(
        FacultySubjectMapping.faculty_id == current_user.id,
        FacultySubjectMapping.subject_id == subject_id
    )
    result = await db.execute(query)
    mapping = result.scalars().first()
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
        
    await db.delete(mapping)
    await db.commit()
    return {"message": "Subject unmapped successfully"}
