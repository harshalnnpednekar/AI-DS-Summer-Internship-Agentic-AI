import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Uuid, func
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    date = Column("event_date", Date, nullable=False)
    department = Column(String(100), nullable=False)
    audience = Column(String(50), nullable=False)  # stores AudienceType

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    department = Column(String(100), nullable=False)

class SendLog(Base):
    __tablename__ = "send_logs"

    log_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    event_id = Column(Uuid, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    student_email = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # stores StatusType
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
