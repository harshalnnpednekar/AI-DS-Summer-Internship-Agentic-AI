import uuid
import enum
from sqlalchemy import Column, Integer, Date, String, DateTime, ForeignKey, Enum, Uuid, func
from sqlalchemy.orm import relationship
from app.database import Base

class CertificateCategoryEnum(str, enum.Enum):
    hackathon = "hackathon"
    workshop = "workshop"
    competition = "competition"
    certification = "certification"
    other = "other"

class VerificationStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    event_name = Column(String(255), nullable=False)
    category = Column(Enum(CertificateCategoryEnum), nullable=False)
    issuing_body = Column(String(255), nullable=False)
    date_achieved = Column(Date, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_kb = Column(Integer, nullable=False)
    verification_status = Column(Enum(VerificationStatusEnum), nullable=False, default=VerificationStatusEnum.pending)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_by = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("StudentProfile")
    verifier = relationship("User")
