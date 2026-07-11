from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import User, RoleEnum, Attendance, DefaulterList, StudentProfile
from ..dependencies import RoleChecker
from ..schemas_omnisync import StandardResponse, DefaulterListCreate, DefaulterListResponse

router = APIRouter(
    prefix="/api/defaulter",
    tags=["OmniSync Defaulters"],
)

allow_hod = RoleChecker([RoleEnum.HOD])

@router.post("/generate", response_model=StandardResponse)
def generate_defaulter_list(
    division: str,
    month: str,
    current_user: User = Depends(allow_hod),
    db: Session = Depends(get_db)
):
    # Here we would normally calculate the attendance percentage for the given month and division
    # For now, let's just find all students in that division and arbitrarily pick some for the simulation.
    
    students = db.query(StudentProfile).filter(StudentProfile.division == division).all()
    
    # Simulate calculating defaulters (e.g., first 2 students)
    defaulter_ids = [str(s.user_id) for s in students[:2]] if students else []
    
    new_defaulter_list = DefaulterList(
        generated_by=current_user.id,
        division=division,
        month=month,
        student_ids=defaulter_ids,
        broadcast_status="PENDING"
    )
    db.add(new_defaulter_list)
    db.commit()
    db.refresh(new_defaulter_list)
    
    return StandardResponse(
        success=True,
        data=DefaulterListResponse.model_validate(new_defaulter_list),
        error=None
    )

@router.post("/broadcast/{list_id}", response_model=StandardResponse)
def broadcast_defaulter_list(
    list_id: str,
    current_user: User = Depends(allow_hod),
    db: Session = Depends(get_db)
):
    defaulter_list = db.query(DefaulterList).filter(DefaulterList.id == list_id).first()
    if not defaulter_list:
         return StandardResponse(
            success=False,
            data=None,
            error="Defaulter list not found"
        )
        
    defaulter_list.broadcast_status = "SENT"
    db.commit()
    db.refresh(defaulter_list)
    
    return StandardResponse(
        success=True,
        data=DefaulterListResponse.model_validate(defaulter_list),
        error=None
    )
