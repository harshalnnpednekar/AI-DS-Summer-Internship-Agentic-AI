import asyncio
import sys
import uuid
from sqlalchemy.future import select
from app.database import SessionLocal
from app.models import User, RoleEnum, Class, Subject, FacultySubjectMapping, FacultyProfile

async def seed_attendance_data():
    async with SessionLocal() as db:
        # Find HOD
        hod_user = await db.execute(
            select(User).where(User.email == "hod.aids@ves.ac.in")
        )
        hod = hod_user.scalars().first()
        if not hod:
            print("HOD not found. Run seed_users.py first.")
            return

        # Find Faculty
        faculty_user = await db.execute(
            select(User).where(User.email == "priya.mehta@ves.ac.in")
        )
        faculty = faculty_user.scalars().first()
        if not faculty:
            print("Faculty not found. Run seed_users.py first.")
            return

        # Create Classes
        c1 = Class(name="SE-A", department_id="AIDS", total_students=60)
        c2 = Class(name="TE-A", department_id="AIDS", total_students=65)
        db.add_all([c1, c2])
        await db.flush()

        # Create Subjects
        s1 = Subject(code="DS101", name="Data Structures & Algorithms", department_id="AIDS")
        s2 = Subject(code="AI101", name="Artificial Intelligence", department_id="AIDS")
        db.add_all([s1, s2])
        await db.flush()

        # Create Mappings for Faculty (Dr. Priya Mehta)
        m1 = FacultySubjectMapping(faculty_id=faculty.id, class_id=c1.id, subject_id=s1.id)
        m2 = FacultySubjectMapping(faculty_id=faculty.id, class_id=c2.id, subject_id=s2.id)
        db.add_all([m1, m2])
        
        await db.commit()
        print("Classes, Subjects, and Mappings seeded successfully!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_attendance_data())
