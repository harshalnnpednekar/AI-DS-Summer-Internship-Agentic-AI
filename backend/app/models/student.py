import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Uuid, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class StudentStatusEnum(str, enum.Enum):
    enrolled = "enrolled"
    graduated = "graduated"
    inactive = "inactive"

class EnrollmentStatusEnum(str, enum.Enum):
    active = "active"
    completed = "completed"
    withdrawn = "withdrawn"

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    department_id = Column(Uuid, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    roll_number = Column(String(50), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    admission_year = Column(Integer, nullable=False)
    graduation_year = Column(Integer, nullable=True)
    status = Column(Enum(StudentStatusEnum), nullable=False, default=StudentStatusEnum.enrolled)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    department = relationship("Department")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Uuid, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Uuid, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    status = Column(Enum(EnrollmentStatusEnum), nullable=False, default=EnrollmentStatusEnum.active)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="enrollments")
    class_obj = relationship("Class")
    academic_year = relationship("AcademicYear")

    __table_args__ = (
        UniqueConstraint(
            "student_id", "academic_year_id", "semester",
            name="uq_student_academic_period_enrollment"
        ),
    )

# Register back_populates on User
from app.models.user import User
User.student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
StudentProfile.enrollments = relationship("Enrollment", back_populates="student")
