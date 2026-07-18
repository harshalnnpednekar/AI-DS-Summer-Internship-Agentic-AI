import uuid
from sqlalchemy import Column, String, DateTime, Uuid, func
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
