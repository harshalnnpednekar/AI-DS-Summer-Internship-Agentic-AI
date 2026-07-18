from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.certificate import CertificateCategoryEnum, VerificationStatusEnum

class CertificateBase(BaseModel):
    title: str
    event_name: str
    category: CertificateCategoryEnum
    issuing_body: str
    date_achieved: date

class CertificateCreate(CertificateBase):
    pass

class CertificateResponse(CertificateBase):
    id: UUID
    student_id: UUID
    file_path: str
    file_size_kb: int
    verification_status: VerificationStatusEnum
    uploaded_at: datetime
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    model_config = {'from_attributes': True}
