import uuid
import enum
from sqlalchemy import Column, String, Date, Time, Integer, DateTime, ForeignKey, Enum, Uuid, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class AttendanceStatusEnum(str, enum.Enum):
    present = "present"
    absent = "absent"
    excused = "excused"

class AttendanceSession(Base):
    """
    Represents a single teaching session where attendance is taken.
    Replaces the old `lecture_attendances` table while maintaining
    the same JSON payload shape for backward-compatible frontend queries.
    """
    __tablename__ = "attendance_sessions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    # Optional FK to class_subjects (may be null for legacy-migrated data)
    class_subject_id = Column(Uuid, ForeignKey("class_subjects.id", ondelete="CASCADE"), nullable=True)
    # Denormalised FKs retained for direct querying (backward compat)
    faculty_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Uuid, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    created_by = Column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Preserved compatibility metadata
    time_slot = Column(String(50), nullable=True)
    topic_covered = Column(String(200), nullable=True)
    total_students_enrolled = Column(Integer, nullable=False, server_default="0")
    students_present_count = Column(Integer, nullable=False, server_default="0")
    absentee_roll_numbers = Column(JSONB, nullable=True)
    session_type = Column(String(20), nullable=False, default="Theory")
    academic_year = Column(String(20), nullable=False, default="2026-2027")
    semester = Column(String(10), nullable=False, default="1")

    # Relationships
    class_subject = relationship("ClassSubject")
    creator = relationship("User", foreign_keys=[created_by])
    faculty = relationship("User", foreign_keys=[faculty_id])
    class_obj = relationship("Class")
    subject = relationship("Subject")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    attendance_session_id = Column(Uuid, ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Uuid, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AttendanceStatusEnum), nullable=False)
    marked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("StudentProfile")

    __table_args__ = (
        UniqueConstraint("attendance_session_id", "student_id", name="uq_attendance_session_student"),
    )

AttendanceSession.records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")
