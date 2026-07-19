import asyncio, sys
sys.path.insert(0, '/app')

async def seed():
    from app.database import SessionLocal
    from app.models import User, RoleEnum, FacultyProfile, StudentProfile
    from app.auth import get_password_hash
    from sqlalchemy.future import select

    async with SessionLocal() as db:
        users = [
            {
                'email': 'hod.aids@ves.ac.in',
                'password': 'hod@123',
                'first_name': 'Dr. M.',
                'last_name': 'Vijayalakshmi',
                'role': RoleEnum.hod,
                'profile_type': 'faculty',
                'dept': 'AIDS',
                'designation': 'HOD',
                'classes': 'SE-A,TE-A',
            },
            {
                'email': 'priya.mehta@ves.ac.in',
                'password': 'faculty@123',
                'first_name': 'Dr. Priya',
                'last_name': 'Mehta',
                'role': RoleEnum.faculty,
                'profile_type': 'faculty',
                'dept': 'AIDS',
                'designation': 'Assistant Professor',
                'classes': 'SE-A,TE-A',
            },
            {
                'email': 'student1@ves.ac.in',
                'password': 'student@123',
                'first_name': 'Test',
                'last_name': 'Student',
                'role': RoleEnum.student,
                'profile_type': 'student',
                'roll': 'SE2021001',
                'dept': 'AIDS',
                'semester': '4',
                'division': 'SE-A',
            },
        ]
        for u in users:
            email = u['email']
            res = await db.execute(select(User).where(User.email == email))
            if res.scalars().first():
                print('EXISTS: ' + email)
                continue
            new_user = User(
                email=email,
                password_hash=get_password_hash(u['password']),
                first_name=u['first_name'],
                last_name=u['last_name'],
                role=u['role']
            )
            db.add(new_user)
            await db.flush()
            if u['profile_type'] == 'faculty':
                prof = FacultyProfile(
                    user_id=new_user.id,
                    department=u['dept'],
                    designation=u['designation'],
                    assigned_classes=u['classes']
                )
            else:
                prof = StudentProfile(
                    user_id=new_user.id,
                    roll_number=u['roll'],
                    department=u['dept'],
                    current_semester=u['semester'],
                    division=u['division']
                )
            db.add(prof)
            print('CREATED: ' + email)
        await db.commit()
        print('Seeding complete!')

asyncio.run(seed())
