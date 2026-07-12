from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict
from typing import Optional, List
from datetime import date as PyDate, datetime
from uuid import UUID
from enum import Enum

# Enums for validation
class EventType(str, Enum):
    exam = "exam"
    holiday = "holiday"
    submission = "submission"
    other = "other"

class AudienceType(str, Enum):
    students = "students"
    faculty = "faculty"
    staff = "staff"
    public = "public"
    all = "ALL"
    all_students = "all_students"

class StatusType(str, Enum):
    sent = "sent"
    failed = "failed"

# Pydantic Models for Events
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: PyDate = Field(..., description="Event date in YYYY-MM-DD format")
    department: str = Field(..., min_length=1, max_length=100)
    audience: AudienceType

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: Optional[PyDate] = None
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    audience: Optional[AudienceType] = None

class EventResponse(EventBase):
    event_id: UUID

    model_config = ConfigDict(from_attributes=True)

# Pydantic Models for Students
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

    class Config:
        from_attributes = True

# Pydantic Models for Send Logs
class SendLogBase(BaseModel):
    event_id: UUID
    student_email: EmailStr
    status: StatusType

class SendLogCreate(SendLogBase):
    pass

class SendLogResponse(BaseModel):
    log_id: UUID
    event_id: UUID
    student_email: str
    status: StatusType
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Bulk Import Model
class EventImport(BaseModel):
    events: List[EventCreate]
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
    phone: Optional[str] = None
    bio: Optional[str] = None
    joining_year: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    assigned_classes: Optional[str] = None

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
    phone: Optional[str] = None
    bio: Optional[str] = None
    joining_year: Optional[str] = None

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
    phone: Optional[str] = None
    bio: Optional[str] = None
    joining_year: Optional[str] = None

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
    time_slot: Optional[str] = None
    topic_covered: str
    total_students_enrolled: int
    students_present_count: int
    absentee_roll_numbers: Optional[List[str]] = []
    session_type: str = "Theory"
