from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models import User, RoleEnum, Attendance, FacultyProfile, StudentProfile
from ..dependencies import get_current_active_user, RoleChecker
from ..schemas_omnisync import StandardResponse, AttendanceCreate, AttendanceResponse

router = APIRouter(
    prefix="/api/attendance",
    tags=["OmniSync Attendance"],
)

allow_faculty_hod = RoleChecker([RoleEnum.FACULTY, RoleEnum.HOD])
allow_all = RoleChecker([RoleEnum.FACULTY, RoleEnum.HOD, RoleEnum.STUDENT])

@router.post("/submit", response_model=StandardResponse)
def submit_attendance(
    attendance: AttendanceCreate, 
    current_user: User = Depends(allow_faculty_hod), 
    db: Session = Depends(get_db)
):
    if current_user.role == RoleEnum.FACULTY:
        faculty_profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
        if not faculty_profile or attendance.division not in (faculty_profile.assigned_classes or ""):
            return StandardResponse(
                success=False,
                data=None,
                error="You are not authorized to submit attendance for this division."
            )
            
    new_attendance = Attendance(
        date=attendance.date,
        subject=attendance.subject,
        faculty_id=current_user.id,
        division=attendance.division,
        status=attendance.status
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    return StandardResponse(
        success=True,
        data=AttendanceResponse.model_validate(new_attendance),
        error=None
    )

@router.get("/student/{student_id}", response_model=StandardResponse)
def get_student_attendance(
    student_id: uuid.UUID,
    current_user: User = Depends(allow_all),
    db: Session = Depends(get_db)
):
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
    if not student_profile:
         return StandardResponse(
            success=False,
            data=None,
            error="Student not found"
        )
        
    if current_user.role == RoleEnum.STUDENT and current_user.id != student_id:
        return StandardResponse(
            success=False,
            data=None,
            error="Students can only view their own attendance"
        )
        
    if current_user.role == RoleEnum.FACULTY:
        faculty_profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
        if not faculty_profile or student_profile.division not in (faculty_profile.assigned_classes or ""):
            return StandardResponse(
                success=False,
                data=None,
                error="You can only view attendance for students in your assigned divisions"
            )

    # In PostgreSQL we can query inside JSONB, but simpler to just query by division and filter in code for now
    # or query all attendance for that division and check if student is in the status dictionary
    # For a robust solution we'd use SQLAlchemy jsonb contains, but let's do a simple approach.
    
    attendances = db.query(Attendance).filter(Attendance.division == student_profile.division).all()
    
    student_records = []
    for att in attendances:
        if str(student_id) in att.status:
            student_records.append({
                "date": att.date,
                "subject": att.subject,
                "status": att.status[str(student_id)]
            })
            
    return StandardResponse(
        success=True,
        data={"records": student_records},
        error=None
    )
