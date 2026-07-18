from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date
from app.models.kt import KTStatusEnum

class KTRecordBase(BaseModel):
    student_id: UUID
    subject_id: UUID
    academic_year_id: UUID
    semester: int
    status: KTStatusEnum = KTStatusEnum.pending
    attempt_count: int = Field(default=1, ge=1)
    cleared_date: Optional[date] = None

class KTRecordCreate(KTRecordBase):
    pass

class KTRecordResponse(KTRecordBase):
    id: UUID
    model_config = {'from_attributes': True}
