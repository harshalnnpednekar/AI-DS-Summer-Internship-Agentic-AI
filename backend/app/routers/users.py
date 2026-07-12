from app import crud
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, FacultyProfile, StudentProfile, RoleEnum
from app.schemas import StudentResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/department/{department}")
async def get_users_by_department(
    department: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all users (HOD, Faculty, Students) for a specific department.
    If department is 'ALL', returns all users.
    """
    try:
        users_list = []
        
        # 1. Fetch Students
        student_query = select(User, StudentProfile).join(StudentProfile, User.id == StudentProfile.user_id)
        if department != "ALL":
            student_query = student_query.where(StudentProfile.department == department)
            
        student_results = await db.execute(student_query)
        for user, profile in student_results.all():
            users_list.append({
                "id": str(user.id),
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.role.value,
                "department": profile.department
            })

        # 2. Fetch Faculty and HOD
        faculty_query = select(User, FacultyProfile).join(FacultyProfile, User.id == FacultyProfile.user_id)
        if department != "ALL":
            faculty_query = faculty_query.where(FacultyProfile.department == department)
            
        faculty_results = await db.execute(faculty_query)
        for user, profile in faculty_results.all():
            users_list.append({
                "id": str(user.id),
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.role.value,
                "department": profile.department
            })
            
        return users_list

    except Exception as e:
        logger.error(f"Error fetching users by department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve users."
        )


logger = logging.getLogger(__name__)


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
