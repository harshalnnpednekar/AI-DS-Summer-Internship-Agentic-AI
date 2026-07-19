from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import User, FacultyProfile, StudentProfile, RoleEnum, Department
from app.auth import verify_password, create_access_token
from app.config import settings
from app.schemas import StandardResponse, UserSignup, ProfileUpdate, UserResponse
from app.services.auth_service import register_user
from app.dependencies.auth import get_current_active_user

router = APIRouter(
    prefix="/api/auth",
    tags=["OmniSync Auth"],
)

@router.post("/login", response_model=StandardResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username.lower()))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.password_hash):
        return StandardResponse(
            success=False,
            data=None,
            error="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires
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
                "role": user.role.value.upper()
            }
        }
    )

@router.post("/signup", response_model=StandardResponse)
async def signup(user_data: UserSignup, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_data)

@router.post("/logout", response_model=StandardResponse)
def logout():
    return StandardResponse(
        success=True,
        data={"message": "Logged out successfully. Please remove your token."},
        error=None
    )

@router.get("/me", response_model=StandardResponse)
async def get_me(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    profile_data = {}
    
    if current_user.role in [RoleEnum.hod, RoleEnum.faculty]:
        profile_result = await db.execute(
            select(FacultyProfile)
            .options(selectinload(FacultyProfile.department))
            .where(FacultyProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            profile_data = {
                "department": profile.department.code,
                "designation": profile.designation,
                "assigned_classes": None, # Will be handled by class_subjects mappings
                "phone": profile.phone if hasattr(profile, 'phone') else None,
                "bio": profile.bio if hasattr(profile, 'bio') else None,
                "joining_year": profile.joining_year if hasattr(profile, 'joining_year') else None,
            }
    elif current_user.role == RoleEnum.student:  # type: ignore
        profile_result = await db.execute(
            select(StudentProfile)
            .options(selectinload(StudentProfile.department))
            .where(StudentProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            profile_data = {
                "department": profile.department.code,
                "roll_number": profile.roll_number,
                "current_semester": "1", # Default value, updated via enrollment
                "division": "A", # Default value, updated via enrollment
                "phone": profile.phone if hasattr(profile, 'phone') else None,
                "bio": profile.bio if hasattr(profile, 'bio') else None,
                "joining_year": str(profile.admission_year),
            }

    return StandardResponse(
        success=True,
        data={
            "id": str(current_user.id),
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "role": current_user.role.value.upper(),
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
    if profile_data.first_name is not None:
        current_user.first_name = profile_data.first_name  # type: ignore
    if profile_data.last_name is not None:
        current_user.last_name = profile_data.last_name  # type: ignore
    
    if current_user.role in [RoleEnum.hod, RoleEnum.faculty]:
        profile_result = await db.execute(
            select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            if profile_data.phone is not None and hasattr(profile, 'phone'): profile.phone = profile_data.phone
            if profile_data.bio is not None and hasattr(profile, 'bio'): profile.bio = profile_data.bio
            if profile_data.designation is not None and hasattr(profile, 'designation'): profile.designation = profile_data.designation  # type: ignore
            if profile_data.department is not None and hasattr(profile, 'department'): profile.department = profile_data.department
            if profile_data.assigned_classes is not None and hasattr(profile, 'assigned_classes'): profile.assigned_classes = profile_data.assigned_classes
            if profile_data.joining_year is not None and hasattr(profile, 'joining_year'): profile.joining_year = profile_data.joining_year  # type: ignore
    
    elif current_user.role == RoleEnum.student:  # type: ignore
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == current_user.id)
        )
        profile = profile_result.scalars().first()
        if profile:
            if profile_data.phone is not None and hasattr(profile, 'phone'): profile.phone = profile_data.phone
            if profile_data.bio is not None and hasattr(profile, 'bio'): profile.bio = profile_data.bio
            if profile_data.department is not None and hasattr(profile, 'department'): profile.department = profile_data.department
            if profile_data.joining_year is not None and hasattr(profile, 'joining_year'): profile.joining_year = profile_data.joining_year  # type: ignore

    await db.commit()
    return StandardResponse(success=True, data={"message": "Profile updated successfully"}, error=None)

@router.post("/repair-profile", response_model=StandardResponse)
async def repair_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role not in [RoleEnum.hod, RoleEnum.faculty]:
        return StandardResponse(success=False, data=None, error="Only HOD/Faculty accounts need profiles.")

    existing = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
    )
    if existing.scalars().first():
        return StandardResponse(success=True, data={"message": "Profile already exists."}, error=None)

    dept_result = await db.execute(select(Department).where(Department.code == "AIDS"))
    dept = dept_result.scalars().first()
    if not dept:
        dept = Department(code="AIDS", name="Artificial Intelligence and Data Science")
        db.add(dept)
        await db.flush()

    profile = FacultyProfile(
        user_id=current_user.id,
        department_id=dept.id,
        designation="HOD" if current_user.role == RoleEnum.hod else "Faculty",  # type: ignore
        employee_code=None,
        full_name=f"{current_user.first_name} {current_user.last_name}"
    )
    db.add(profile)
    await db.commit()
    return StandardResponse(success=True, data={"message": "Profile created successfully. Refresh the dashboard."}, error=None)
