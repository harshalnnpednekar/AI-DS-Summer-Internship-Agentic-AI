from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import date as PyDate, datetime
from uuid import UUID
import enum

class EventType(str, enum.Enum):
    exam = "exam"
    holiday = "holiday"
    submission = "submission"
    other = "other"

class AudienceType(str, enum.Enum):
    students = "students"
    faculty = "faculty"
    staff = "staff"
    public = "public"
    all = "ALL"
    all_students = "all_students"

class StatusType(str, enum.Enum):
    sent = "sent"
    failed = "failed"

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

class EventImport(BaseModel):
    events: List[EventCreate]
