from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from app.models.user import RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserSignup(UserBase):
    password: str
    department: Optional[str] = None
    designation: Optional[str] = None
    assigned_classes: Optional[str] = None
    roll_number: Optional[str] = None
    current_semester: Optional[str] = None
    division: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    joining_year: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    role: str  # We return it as a string (capitalized) for frontend compatibility
    created_at: datetime
    updated_at: datetime

    # Custom serializer to capitalize the role for the frontend
    @classmethod
    def model_validate(cls, obj: Any, *args, **kwargs):
        validated = super().model_validate(obj, *args, **kwargs)
        if isinstance(validated.role, RoleEnum):
            validated.role = validated.role.value.upper()
        elif isinstance(validated.role, str):
            validated.role = validated.role.upper()
        return validated

    model_config = {'from_attributes': True}

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    assigned_classes: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[RoleEnum] = None

class StandardResponse(BaseModel):
    success: bool
    data: Any = None
    error: Optional[str] = None
