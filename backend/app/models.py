import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Uuid, func
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    date = Column("event_date", Date, nullable=False)
    department = Column(String(100), nullable=False)
    audience = Column(String(50), nullable=False)  # stores AudienceType

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    department = Column(String(100), nullable=False)

class SendLog(Base):
    __tablename__ = "send_logs"

    log_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    event_id = Column(Uuid, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    student_email = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # stores StatusType
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# --- OmniSync Models ---

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB
import enum

class RoleEnum(str, enum.Enum):
    HOD = "HOD"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    assigned_classes = Column(String(100), nullable=True) # E.g., "SE-A"

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    roll_number = Column(String(50), nullable=False, unique=True)
    department = Column(String(100), nullable=False)
    current_semester = Column(String(20), nullable=False)
    division = Column(String(50), nullable=False)

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)
    subject = Column(String(100), nullable=False)
    faculty_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    division = Column(String(50), nullable=False)
    status = Column(JSONB, nullable=False) # Maps student ID to Present/Absent

class DefaulterList(Base):
    __tablename__ = "defaulter_lists"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    generated_by = Column(Uuid, ForeignKey("users.id"), nullable=False)
    division = Column(String(50), nullable=False)
    month = Column(String(20), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    student_ids = Column(JSONB, nullable=False) # Array of student IDs
    broadcast_status = Column(String(20), nullable=False, default="PENDING")

from sqlalchemy import Integer

class Class(Base):
    __tablename__ = "classes"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    department_id = Column(String(100), nullable=False)
    total_students = Column(Integer, nullable=False, default=0)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    department_id = Column(String(100), nullable=False)

class FacultySubjectMapping(Base):
    __tablename__ = "faculty_subject_mappings"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    faculty_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Uuid, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

class LectureAttendance(Base):
    __tablename__ = "lecture_attendances"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    faculty_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Uuid, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    lecture_date = Column(Date, nullable=False)
    topic_covered = Column(String(200), nullable=False)
    total_students_enrolled = Column(Integer, nullable=False)
    students_present_count = Column(Integer, nullable=False)
    absentee_roll_numbers = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
