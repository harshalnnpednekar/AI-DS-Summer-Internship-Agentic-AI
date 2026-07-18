from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from decimal import Decimal
from app.models.grade import GradeResultEnum

class GradeBase(BaseModel):
    student_id: UUID
    subject_id: UUID
    academic_year_id: UUID
    semester: int
    internal_marks: Decimal = Field(default=0, ge=0)
    external_marks: Decimal = Field(default=0, ge=0)
    total_marks: Decimal = Field(default=0, ge=0)
    grade_letter: str = Field(..., max_length=5)
    grade_point: Decimal = Field(default=0, ge=0)
    result_status: GradeResultEnum

class GradeCreate(GradeBase):
    pass

class GradeResponse(GradeBase):
    id: UUID
    model_config = {'from_attributes': True}
