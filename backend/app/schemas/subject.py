from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class SubjectBase(BaseModel):
    code: str
    name: str
    department_id: UUID
    semester: int
    credits: int
    is_active: bool = True

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: UUID
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
