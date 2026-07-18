from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, FacultyProfile, StudentProfile, RoleEnum, Department
from app.auth import verify_password, get_password_hash, create_access_token
from app.config import settings
from app.schemas import UserSignup, StandardResponse

async def register_user(db: AsyncSession, signup_data: UserSignup) -> StandardResponse:
    # Check if email is already taken
    result = await db.execute(select(User).where(User.email == signup_data.email.lower()))
    if result.scalars().first():
        return StandardResponse(success=False, data=None, error="Email already registered")
    
    # 1. Standardise and lowercase role input (RoleEnum._missing_ converts case-insensitively)
    role_enum = RoleEnum(signup_data.role)
    if not role_enum:
        return StandardResponse(success=False, data=None, error=f"Invalid role: {signup_data.role}")

    # 2. Create the main User record
    new_user = User(
        email=signup_data.email.lower(),
        password_hash=get_password_hash(signup_data.password),
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        role=role_enum
    )
    db.add(new_user)
    await db.flush()  # to get new_user.id

    # 3. Lookup department by code (e.g. "AIDS" or "General" as fallback)
    dept_code = signup_data.department or "General"
    dept_result = await db.execute(select(Department).where(Department.code == dept_code))
    dept = dept_result.scalars().first()
    if not dept:
        # Create department on the fly if it doesn't exist to make dev/seeding/tests seamless
        dept = Department(code=dept_code, name=f"{dept_code} Department")
        db.add(dept)
        await db.flush()

    # 4. Create role-specific profiles
    if role_enum in [RoleEnum.faculty, RoleEnum.hod]:
        profile = FacultyProfile(
            user_id=new_user.id,
            department_id=dept.id,
            designation=signup_data.designation or ("HOD" if role_enum == RoleEnum.hod else "Faculty"),
            employee_code=None,  # Or mapping if provided
            full_name=f"{signup_data.first_name} {signup_data.last_name}"
        )
        db.add(profile)
    elif role_enum == RoleEnum.student:
        profile = StudentProfile(
            user_id=new_user.id,
            department_id=dept.id,
            roll_number=signup_data.roll_number or f"TMP-{new_user.id.hex[:8]}",
            full_name=f"{signup_data.first_name} {signup_data.last_name}",
            admission_year=int(signup_data.joining_year or datetime.now().year),
            graduation_year=None,
            status="enrolled"
        )
        db.add(profile)

    await db.commit()

    # 5. Generate Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role.value}, expires_delta=access_token_expires
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
                "role": new_user.role.value.upper()  # capitalize for frontend compatibility
            }
        }
    )
