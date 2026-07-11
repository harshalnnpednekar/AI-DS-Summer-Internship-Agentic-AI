from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import User, FacultyProfile, StudentProfile, RoleEnum
from ..auth import verify_password, create_access_token, get_password_hash
from ..config import settings
from ..schemas_omnisync import StandardResponse, Token, UserSignup

router = APIRouter(
    prefix="/api/auth",
    tags=["OmniSync Auth"],
)

@router.post("/login", response_model=StandardResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.password_hash):
        return StandardResponse(
            success=False,
            data=None,
            error="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    
    return StandardResponse(
        success=True,
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role
            }
        }
    )

@router.post("/signup", response_model=StandardResponse)
async def signup(user_data: UserSignup, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        return StandardResponse(
            success=False,
            data=None,
            error="Email already registered"
        )
        
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    if user_data.role == RoleEnum.FACULTY:
        profile = FacultyProfile(
            user_id=new_user.id,
            department=user_data.department or "General",
            designation=user_data.designation or "Faculty",
            assigned_classes=user_data.assigned_classes
        )
        db.add(profile)
    elif user_data.role == RoleEnum.STUDENT:
        profile = StudentProfile(
            user_id=new_user.id,
            roll_number=user_data.roll_number or f"TMP-{new_user.id}",
            department=user_data.department or "General",
            current_semester=user_data.current_semester or "1",
            division=user_data.division or "A"
        )
        db.add(profile)
        
    await db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role}, expires_delta=access_token_expires
    )
    
    return StandardResponse(
        success=True,
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "role": new_user.role
            }
        }
    )

@router.post("/logout", response_model=StandardResponse)
def logout():
    # Since we are using stateless JWT, we just tell the client to remove the token.
    return StandardResponse(
        success=True,
        data={"message": "Logged out successfully. Please remove your token."},
        error=None
    )
