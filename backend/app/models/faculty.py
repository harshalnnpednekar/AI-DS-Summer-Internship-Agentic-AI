import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import relationship
from app.database import Base

class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    department_id = Column(Uuid, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    employee_code = Column(String(50), nullable=True, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    designation = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department")

# Register back_populates on User
from app.models.user import User
User.faculty_profile = relationship("FacultyProfile", back_populates="user", uselist=False)
