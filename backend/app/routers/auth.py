from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import User, FacultyProfile, StudentProfile, RoleEnum
from ..auth import verify_password, create_access_token, get_password_hash
from ..config import settings
from ..schemas import StandardResponse, Token, UserSignup, ProfileUpdate

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
    
    if user_data.role in [RoleEnum.FACULTY, RoleEnum.HOD]:
        profile = FacultyProfile(
            user_id=new_user.id,
            department=user_data.department or "General",
            designation=user_data.designation or ("HOD" if user_data.role == RoleEnum.HOD else "Faculty"),
            assigned_classes=user_data.assigned_classes,
            phone=user_data.phone,
            bio=user_data.bio,
            joining_year=user_data.joining_year
        )
        db.add(profile)
    elif user_data.role == RoleEnum.STUDENT:
        profile = StudentProfile(
            user_id=new_user.id,
            roll_number=user_data.roll_number or f"TMP-{new_user.id}",
            department=user_data.department or "General",
            current_semester=user_data.current_semester or "1",
            division=user_data.division or "A",
            phone=user_data.phone,
            bio=user_data.bio,
            joining_year=user_data.joining_year
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

from ..dependencies import get_current_active_user

@router.get("/me", response_model=StandardResponse)
async def get_me(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    profile_data = {}
    if current_user.role in [RoleEnum.HOD, RoleEnum.FACULTY]:
        profile_result = await db.execute(
            select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            profile_data = {
                "department": profile.department,
                "designation": profile.designation,
                "assigned_classes": profile.assigned_classes,
                "phone": profile.phone,
                "bio": profile.bio,
                "joining_year": profile.joining_year,
            }
    elif current_user.role == RoleEnum.STUDENT:
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            profile_data = {
                "department": profile.department,
                "roll_number": profile.roll_number,
                "current_semester": profile.current_semester,
                "division": profile.division,
                "phone": profile.phone,
                "bio": profile.bio,
                "joining_year": profile.joining_year,
            }

    return StandardResponse(
        success=True,
        data={
            "id": str(current_user.id),
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat(),
            **profile_data
        },
        error=None
    )

@router.put("/me", response_model=StandardResponse)
async def update_me(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Update basic user fields
    if profile_data.first_name is not None:
        current_user.first_name = profile_data.first_name
    if profile_data.last_name is not None:
        current_user.last_name = profile_data.last_name
    
    # Update role-specific profile fields
    if current_user.role in [RoleEnum.HOD, RoleEnum.FACULTY]:
        profile_result = await db.execute(
            select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            if profile_data.phone is not None: profile.phone = profile_data.phone
            if profile_data.bio is not None: profile.bio = profile_data.bio
            if profile_data.designation is not None: profile.designation = profile_data.designation
            if profile_data.department is not None: profile.department = profile_data.department
            if profile_data.assigned_classes is not None: profile.assigned_classes = profile_data.assigned_classes
            if profile_data.joining_year is not None: profile.joining_year = profile_data.joining_year
    
    elif current_user.role == RoleEnum.STUDENT:
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            if profile_data.phone is not None: profile.phone = profile_data.phone
            if profile_data.bio is not None: profile.bio = profile_data.bio
            if profile_data.department is not None: profile.department = profile_data.department
            if profile_data.joining_year is not None: profile.joining_year = profile_data.joining_year

    await db.commit()
    return StandardResponse(success=True, data={"message": "Profile updated successfully"}, error=None)



@router.post("/repair-profile", response_model=StandardResponse)
async def repair_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a missing faculty_profile row for HOD/Faculty users who registered before the fix."""
    if current_user.role not in [RoleEnum.HOD, RoleEnum.FACULTY]:
        return StandardResponse(success=False, data=None, error="Only HOD/Faculty accounts need profiles.")

    existing = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
    )
    if existing.scalars().first():
        return StandardResponse(success=True, data={"message": "Profile already exists."}, error=None)

    profile = FacultyProfile(
        user_id=current_user.id,
        department="AIDS",
        designation="HOD" if current_user.role == RoleEnum.HOD else "Faculty",
        assigned_classes=None
    )
    db.add(profile)
    await db.commit()
    return StandardResponse(success=True, data={"message": "Profile created successfully. Refresh the dashboard."}, error=None)
