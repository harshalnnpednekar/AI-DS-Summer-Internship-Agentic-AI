from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.student import StudentStatusEnum, EnrollmentStatusEnum

# Base student models (retained from old events model schema for email recipient mapping)
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=100)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=1, max_length=100)

class StudentResponse(StudentBase):
    student_id: UUID
    model_config = {'from_attributes': True}

# Profile models
class StudentProfileBase(BaseModel):
    roll_number: str
    department: str
    current_semester: str
    division: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    joining_year: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileResponse(StudentProfileBase):
    id: UUID
    user_id: UUID
    status: StudentStatusEnum
    model_config = {'from_attributes': True}

# Enrollment models
class EnrollmentBase(BaseModel):
    student_id: UUID
    class_id: UUID
    academic_year_id: UUID
    semester: int
    status: EnrollmentStatusEnum

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentResponse(EnrollmentBase):
    id: UUID
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    model_config = {'from_attributes': True}
