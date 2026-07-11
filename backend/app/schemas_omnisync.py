from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
import enum
from .models import RoleEnum

# --- User Schemas ---

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserSignup(UserBase):
    password: str
    department: Optional[str] = None
    designation: Optional[str] = None
    assigned_classes: Optional[str] = None
    roll_number: Optional[str] = None
    current_semester: Optional[str] = None
    division: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}

# --- Auth Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[RoleEnum] = None

# --- Faculty Schemas ---

class FacultyProfileBase(BaseModel):
    department: str
    designation: str
    assigned_classes: Optional[str] = None

class FacultyProfileCreate(FacultyProfileBase):
    pass

class FacultyProfileResponse(FacultyProfileBase):
    id: UUID
    user_id: UUID

    model_config = {'from_attributes': True}

# --- Student Schemas ---

class StudentProfileBase(BaseModel):
    roll_number: str
    department: str
    current_semester: str
    division: str

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileResponse(StudentProfileBase):
    id: UUID
    user_id: UUID

    model_config = {'from_attributes': True}

# --- Attendance Schemas ---

class AttendanceBase(BaseModel):
    date: date
    subject: str
    division: str
    status: Dict[str, str] # e.g., {"student_id_1": "Present", "student_id_2": "Absent"}

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: UUID
    faculty_id: UUID

    model_config = {'from_attributes': True}

# --- Defaulter Schemas ---

class DefaulterListBase(BaseModel):
    division: str
    month: str
    student_ids: List[str]

class DefaulterListCreate(DefaulterListBase):
    pass

class DefaulterListResponse(DefaulterListBase):
    id: UUID
    generated_by: UUID
    generated_at: datetime
    broadcast_status: str

    model_config = {'from_attributes': True}

class StandardResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None

# --- Lecture Attendance Schemas ---

class LectureAttendanceSubmit(BaseModel):
    class_id: UUID
    subject_id: UUID
    lecture_date: date
    topic_covered: str
    total_students_enrolled: int
    students_present_count: int
    absentee_roll_numbers: Optional[List[str]] = []
