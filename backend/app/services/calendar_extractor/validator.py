from pydantic import BaseModel, Field, field_validator
from typing import List
import uuid
import re

VALID_DEPTS = {"ALL", "AIDS", "EXTC", "IT", "COMS", "ECS", "AURO", "MCA"}

class AcademicEvent(BaseModel):
    event_id: str = Field(..., min_length=1, description="Unique identifier for the event")
    title: str = Field(..., min_length=1, description="Event Title or name of the academic event")
    description: str = Field(..., min_length=1, description="Description of the event")
    date: str = Field(..., min_length=1, description="Date or date range of the event")
    department: str = Field(..., min_length=1, description="Department responsible or involved")
    audience: str = Field(..., min_length=1, description="Target audience for the event")

    @field_validator('event_id')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v, version=4)
        except ValueError:
            raise ValueError(f"'{v}' is not a valid UUID4")
        return v

    @field_validator('date')
    def validate_date_format(cls, v):
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError(f"Date '{v}' must be in strict YYYY-MM-DD format")
        return v

    @field_validator('department')
    def validate_department(cls, v):
        if v not in VALID_DEPTS:
            raise ValueError(f"Invalid department '{v}'. Must be one of {VALID_DEPTS}")
        return v

class EventList(BaseModel):
    events: List[AcademicEvent]
