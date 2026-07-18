from pydantic import BaseModel, Field, model_validator
from typing import Optional
from uuid import UUID

class SubjectBase(BaseModel):
    code: str
    name: str
    department_id: UUID
    year_level: int = Field(ge=1, le=4)
    semester: int = Field(ge=1, le=8)
    credits: int
    is_active: bool = True

    @model_validator(mode="after")
    def validate_year_level_matches_semester(self):
        expected_year_level = (self.semester + 1) // 2
        if self.year_level != expected_year_level:
            raise ValueError(
                "year_level must match semester: 1-2=FE, 3-4=SE, 5-6=TE, 7-8=BE"
            )
        return self

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    department_id: Optional[UUID] = None
    year_level: Optional[int] = Field(default=None, ge=1, le=4)
    semester: Optional[int] = Field(default=None, ge=1, le=8)
    credits: Optional[int] = None
    is_active: Optional[bool] = None

class SubjectResponse(SubjectBase):
    id: UUID
    year: str
    model_config = {'from_attributes': True}

class ClassSubjectBase(BaseModel):
    class_id: UUID
    subject_id: UUID
    faculty_id: Optional[UUID] = None

class ClassSubjectCreate(ClassSubjectBase):
    pass

class ClassSubjectResponse(ClassSubjectBase):
    id: UUID
    model_config = {'from_attributes': True}
