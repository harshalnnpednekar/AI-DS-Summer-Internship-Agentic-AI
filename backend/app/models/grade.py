import uuid
import enum
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, Enum, Uuid, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class GradeResultEnum(str, enum.Enum):
    pass_ = "pass"  # python keyword pass, use pass_ in code
    fail = "fail"
    kt = "kt"

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Uuid, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    internal_marks = Column(Numeric, nullable=False, default=0)
    external_marks = Column(Numeric, nullable=False, default=0)
    total_marks = Column(Numeric, nullable=False, default=0)
    grade_letter = Column(String(5), nullable=False)
    grade_point = Column(Numeric, nullable=False, default=0)
    result_status = Column(Enum(GradeResultEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    student = relationship("StudentProfile")
    subject = relationship("Subject")
    academic_year = relationship("AcademicYear")

    __table_args__ = (
        UniqueConstraint(
            "student_id", "subject_id", "academic_year_id", "semester",
            name="uq_student_subject_attempt"
        ),
    )
