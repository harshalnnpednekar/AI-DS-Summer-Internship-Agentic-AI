import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Uuid, func
from app.database import Base

class RoleEnum(str, enum.Enum):
    student = "student"
    faculty = "faculty"
    hod = "hod"
    admin = "admin"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val = value.lower()
            for member in cls:
                if member.value == val:
                    return member
        return None

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
