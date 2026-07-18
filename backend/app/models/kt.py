import uuid
import enum
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Enum, Uuid, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class KTStatusEnum(str, enum.Enum):
    pending = "pending"
    cleared = "cleared"

class KTRecord(Base):
    __tablename__ = "kt_records"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Uuid, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    status = Column(Enum(KTStatusEnum), nullable=False, default=KTStatusEnum.pending)
    attempt_count = Column(Integer, nullable=False, default=1)
    cleared_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    student = relationship("StudentProfile")
    subject = relationship("Subject")
    academic_year = relationship("AcademicYear")

    # Business rule: Prevent duplicate active pending KT for the same academic subject occurrence.
    # Note: We can have multiple historical cleared ones, but only one active pending.
    # We can enforce this with a partial unique index.
    __table_args__ = (
        UniqueConstraint(
            "student_id", "subject_id", "academic_year_id", "semester",
            name="uq_student_kt_occurrence"
        ),
    )
