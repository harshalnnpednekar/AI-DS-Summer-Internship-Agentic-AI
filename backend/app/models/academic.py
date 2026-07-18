import uuid
from sqlalchemy import Column, String, Date, Integer, Boolean, DateTime, ForeignKey, Uuid, func, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(20), nullable=False, unique=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index(
            "uq_academic_years_current",
            "is_current",
            postgresql_where="is_current = true",
            unique=True
        ),
    )

class Class(Base):
    __tablename__ = "classes"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    department_id = Column(Uuid, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Uuid, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    year_level = Column(Integer, nullable=False)
    division = Column(String(10), nullable=False)
    semester = Column(Integer, nullable=False)
    # Computed display name (e.g. "SE-A") — stored for easy querying
    name = Column(String(50), nullable=True)
    # Total students count for display (legacy field)
    total_students = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    department = relationship("Department")
    academic_year = relationship("AcademicYear")

    __table_args__ = (
        UniqueConstraint(
            "department_id", "academic_year_id", "year_level", "division", "semester",
            name="uq_class_definition"
        ),
    )

