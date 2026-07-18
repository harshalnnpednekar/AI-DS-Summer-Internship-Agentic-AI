from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date
from uuid import UUID
import enum

# Enums
class AcademicYearEnum(str, enum.Enum):
    year_2024_2025 = "2024-2025"
    year_2025_2026 = "2025-2026"
    year_2026_2027 = "2026-2027"
    year_2027_2028 = "2027-2028"

class SemesterEnum(str, enum.Enum):
    sem_1 = "1"
    sem_2 = "2"
    sem_3 = "3"
    sem_4 = "4"
    sem_5 = "5"
    sem_6 = "6"
    sem_7 = "7"
    sem_8 = "8"

# Lecture attendance submission model (used in frontend MarkAttendance page)
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
    academic_year: Optional[AcademicYearEnum] = Field(
        default=None,
        description="Academic year in YYYY-YYYY format; auto-filled when omitted",
    )
    semester: Optional[SemesterEnum] = Field(
        default=None,
        description="Semester number from 1-8; auto-filled when omitted",
    )

# Old attendance schemas (retained for backward compatibility if any service uses them)
class AttendanceBase(BaseModel):
    date: date
    subject: str
    division: str
    status: Dict[str, str]

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: UUID
    faculty_id: UUID
    model_config = {'from_attributes': True}
