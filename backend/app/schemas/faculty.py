from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class FacultyProfileBase(BaseModel):
    department: str
    designation: str
    assigned_classes: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    joining_year: Optional[str] = None

class FacultyProfileCreate(FacultyProfileBase):
    pass

class FacultyProfileResponse(FacultyProfileBase):
    id: UUID
    user_id: UUID
    model_config = {'from_attributes': True}
