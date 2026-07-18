import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Uuid, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    department_id = Column(Uuid, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    credits = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    department = relationship("Department")

class ClassSubject(Base):
    __tablename__ = "class_subjects"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    class_id = Column(Uuid, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Uuid, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    faculty_id = Column(Uuid, ForeignKey("faculty_profiles.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    class_obj = relationship("Class")
    subject = relationship("Subject")
    faculty = relationship("FacultyProfile")

    __table_args__ = (
        UniqueConstraint("class_id", "subject_id", name="uq_class_subject"),
    )
