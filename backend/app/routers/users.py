from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, FacultyProfile, StudentProfile, RoleEnum, Department
from app.schemas import StudentResponse, StandardResponse
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
        
        # 1. Fetch Students joined with their department
        student_query = (
            select(User, StudentProfile, Department)
            .join(StudentProfile, User.id == StudentProfile.user_id)
            .join(Department, StudentProfile.department_id == Department.id)
        )
        if department != "ALL":
            student_query = student_query.where(Department.code == department)
            
        student_results = await db.execute(student_query)
        for user, profile, dept in student_results.all():
            users_list.append({
                "id": str(user.id),
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.role.value.upper(),
                "department": dept.code
            })

        # 2. Fetch Faculty and HOD joined with their department
        faculty_query = (
            select(User, FacultyProfile, Department)
            .join(FacultyProfile, User.id == FacultyProfile.user_id)
            .join(Department, FacultyProfile.department_id == Department.id)
        )
        if department != "ALL":
            faculty_query = faculty_query.where(Department.code == department)
            
        faculty_results = await db.execute(faculty_query)
        for user, profile, dept in faculty_results.all():
            users_list.append({
                "id": str(user.id),
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.role.value.upper(),
                "department": dept.code
            })
            
        return users_list

    except Exception as e:
        logger.error(f"Error fetching users by department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve users."
        )
