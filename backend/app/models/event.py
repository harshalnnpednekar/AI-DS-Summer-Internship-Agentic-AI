import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import relationship
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    date = Column("event_date", Date, nullable=False)
    department = Column(String(100), nullable=False)
    audience = Column(String(50), nullable=False)  # stores AudienceType

    # Extended audit fields
    created_by = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User")
