from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

class DefaulterListBase(BaseModel):
    division: str
    month: str
    student_ids: List[str]

class DefaulterListCreate(DefaulterListBase):
    pass

class DefaulterListResponse(DefaulterListBase):
    id: UUID
    generated_by: UUID
    generated_at: datetime
    broadcast_status: str
    model_config = {'from_attributes': True}
