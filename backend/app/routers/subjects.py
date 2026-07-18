from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models import ClassSubject, FacultyProfile, RoleEnum, Subject, User
from app.schemas import SubjectCreate, SubjectResponse
from app.dependencies.auth import get_current_active_user as get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

YEAR_LEVELS = {"FE": 1, "SE": 2, "TE": 3, "BE": 4}


def require_subject_manager(current_user: User) -> None:
    if current_user.role not in (RoleEnum.hod, RoleEnum.faculty):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


async def get_faculty_profile(db: AsyncSession, current_user: User) -> FacultyProfile:
    result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
    )
    faculty_profile = result.scalars().first()
    if not faculty_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty profile not found")
    return faculty_profile


@router.get("", response_model=List[SubjectResponse])
async def get_subjects(
    year: Optional[str] = None,
    semester: Optional[int] = None,
    department_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Subject)
    if year:
        year_level = YEAR_LEVELS.get(year.upper())
        if year_level is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="year must be one of FE, SE, TE, or BE",
            )
        query = query.where(Subject.year_level == year_level)
    if semester is not None:
        query = query.where(Subject.semester == semester)
    if department_id:
        query = query.where(Subject.department_id == department_id)

    result = await db.execute(query.order_by(Subject.year_level, Subject.semester, Subject.name))
    return result.scalars().all()

@router.post("", response_model=SubjectResponse)
async def create_subject(
    subject: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_subject_manager(current_user)

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
    require_subject_manager(current_user)
    faculty_profile = await get_faculty_profile(db, current_user)

    query = select(Subject).join(ClassSubject, Subject.id == ClassSubject.subject_id) \
                           .where(ClassSubject.faculty_id == faculty_profile.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/faculty/map/{subject_id}")
async def map_faculty_subject(
    subject_id: UUID,
    class_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_subject_manager(current_user)
    faculty_profile = await get_faculty_profile(db, current_user)

    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    mapping = ClassSubject(
        faculty_id=faculty_profile.id,
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
    require_subject_manager(current_user)
    faculty_profile = await get_faculty_profile(db, current_user)

    query = select(ClassSubject).where(
        ClassSubject.faculty_id == faculty_profile.id,
        ClassSubject.subject_id == subject_id
    )
    result = await db.execute(query)
    mapping = result.scalars().first()

    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    await db.delete(mapping)
    await db.commit()
    return {"message": "Subject unmapped successfully"}
