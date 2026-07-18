import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import relationship
from app.database import Base

class SendLog(Base):
    __tablename__ = "send_logs"

    log_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    event_id = Column(Uuid, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=True)
    student_email = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # stores StatusType
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    error_message = Column(String(1000), nullable=True)

    # Relationships
    event = relationship("Event")
