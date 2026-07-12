from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import Student, Event
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test students - exactly two entries with Puneet's emails, in AIDS department
students = [
    {
        "name": "Member1",
        "email": "puneetdhongade26@gmail.com",
        "department": "AIDS"
    },
    {
        "name": "Member2",
        "email": "puneetsdhongade2006@gmail.com",
        "department": "AIDS"
    }
]

# Test events (relative to today)
current_date = datetime.now().date()

events = [
    {
        "title": "Unit Test 1",
        "description": "First unit test covering units 1 and 2",
        "date": current_date + timedelta(days=2),
        "department": "AIDS",
        "audience": "ALL"
    },
    {
        "title": "Assignment Submission Deadline",
        "description": "Final submission for mini project phase 1",
        "date": current_date + timedelta(days=4),
        "department": "AIDS",
        "audience": "ALL"
    },
    {
        "title": "Guest Lecture — AI in Industry",
        "description": "Industry expert session on real-world AI applications",
        "date": current_date + timedelta(days=7),
        "department": "AIDS",
        "audience": "ALL"
    }
]

async def seed_data():
    async with SessionLocal() as db:
        # Seed students
        for student_data in students:
            # Check for duplicate
            result = await db.execute(
                select(Student).where(
                    Student.name == student_data["name"],
                    Student.email == student_data["email"],
                    Student.department == student_data["department"]
                )
            )
            existing_student = result.scalars().first()

            if not existing_student:
                new_student = Student(**student_data)
                db.add(new_student)
                await db.commit()
                await db.refresh(new_student)
                logger.info(f"Inserted Student: {new_student.name} ({new_student.email})")
            else:
                logger.info(f"Student {student_data['name']} already exists.")

        # Seed events
        for event_data in events:
            result = await db.execute(
                select(Event).where(
                    Event.title == event_data["title"],
                    Event.description == event_data["description"],
                    Event.date == event_data["date"],
                    Event.department == event_data["department"],
                    Event.audience == event_data["audience"]
                )
            )
            existing_event = result.scalars().first()

            if not existing_event:
                new_event = Event(**event_data)
                db.add(new_event)
                await db.commit()
                await db.refresh(new_event)
                logger.info(f"Inserted Event: {new_event.title}")
            else:
                logger.info(f"Event '{event_data['title']}' already exists.")

if __name__ == "__main__":
    import asyncio
    import selectors
    selector = selectors.SelectSelector()
    loop = asyncio.SelectorEventLoop(selector)
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(seed_data())
    finally:
        loop.close()
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
