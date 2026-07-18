import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class DefaulterList(Base):
    __tablename__ = "defaulter_lists"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    generated_by = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    division = Column(String(50), nullable=False)
    month = Column(String(20), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    student_ids = Column(JSONB, nullable=False) # Array of student IDs
    broadcast_status = Column(String(20), nullable=False, default="PENDING")

    # Relationships
    creator = relationship("User")
