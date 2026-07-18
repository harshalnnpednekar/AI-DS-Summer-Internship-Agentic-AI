"""
Idempotent seed script for EduAgent Phase 2.

Creates all required demo data if it doesn't already exist:
- Departments (AIDS, CS)
- Academic Year (2025-2026, current)
- Classes (SE-A, SE-B, TE-A, BE-A)
- Subjects per semester
- HOD user + FacultyProfile
- Faculty users + FacultyProfiles
- Student users + StudentProfiles
- ClassSubject mappings
- Events

Run with:  python -m app.seed
"""
import asyncio
import sys
import uuid
import logging
from datetime import datetime, timedelta, date

from sqlalchemy.future import select
from app.database import SessionLocal
from app.models import (
    User, RoleEnum,
    Department,
    AcademicYear, Class,
    StudentProfile,
    FacultyProfile,
    Subject, ClassSubject,
    Event,
)
from app.auth import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_or_create(db, model, filters: dict, defaults: dict = None):
    """Get an existing record or create a new one (idempotent)."""
    stmt = select(model)
    for k, v in filters.items():
        stmt = stmt.where(getattr(model, k) == v)
    result = await db.execute(stmt)
    obj = result.scalars().first()
    if not obj:
        create_kwargs = {**filters, **(defaults or {})}
        obj = model(**create_kwargs)
        db.add(obj)
        await db.flush()
        logger.info(f"Created {model.__name__}: {filters}")
    else:
        logger.info(f"Exists {model.__name__}: {filters}")
    return obj


async def seed():
    async with SessionLocal() as db:

        # ─── 1. Departments ────────────────────────────────────────────────
        aids_dept = await get_or_create(
            db, Department, {"code": "AIDS"},
            {"name": "Artificial Intelligence and Data Science"}
        )
        cs_dept = await get_or_create(
            db, Department, {"code": "CS"},
            {"name": "Computer Science"}
        )

        # ─── 2. Academic Year ──────────────────────────────────────────────
        ay = await get_or_create(
            db, AcademicYear, {"name": "2025-2026"},
            {
                "start_date": date(2025, 7, 1),
                "end_date": date(2026, 6, 30),
                "is_current": True
            }
        )

        # ─── 3. Classes ────────────────────────────────────────────────────
        class_defs = [
            {"year_level": 2, "division": "A", "semester": 3},
            {"year_level": 2, "division": "B", "semester": 3},
            {"year_level": 3, "division": "A", "semester": 5},
            {"year_level": 4, "division": "A", "semester": 7},
        ]
        classes = {}
        for cd in class_defs:
            name = f"{'FE' if cd['year_level']==1 else 'SE' if cd['year_level']==2 else 'TE' if cd['year_level']==3 else 'BE'}-{cd['division']}"
            c = await get_or_create(
                db, Class,
                {"department_id": aids_dept.id, "academic_year_id": ay.id, "year_level": cd["year_level"], "division": cd["division"], "semester": cd["semester"]},
                {"name": name}
            )
            classes[name] = c

        # ─── 4. Subjects ───────────────────────────────────────────────────
        subject_defs = [
            {"code": "AIDS301", "name": "Machine Learning",              "semester": 3, "credits": 4},
            {"code": "AIDS302", "name": "Data Warehousing",              "semester": 3, "credits": 3},
            {"code": "AIDS303", "name": "Python Programming Lab",        "semester": 3, "credits": 2},
            {"code": "AIDS501", "name": "Deep Learning",                 "semester": 5, "credits": 4},
            {"code": "AIDS502", "name": "Natural Language Processing",   "semester": 5, "credits": 4},
            {"code": "AIDS503", "name": "Cloud Computing",               "semester": 5, "credits": 3},
            {"code": "AIDS701", "name": "AI Ethics and Governance",      "semester": 7, "credits": 3},
            {"code": "AIDS702", "name": "Capstone Project",              "semester": 7, "credits": 6},
        ]
        subjects = {}
        for sd in subject_defs:
            s = await get_or_create(
                db, Subject, {"code": sd["code"]},
                {"name": sd["name"], "semester": sd["semester"], "credits": sd["credits"], "department_id": str(aids_dept.id)}
            )
            subjects[sd["code"]] = s

        # ─── 5. HOD User ───────────────────────────────────────────────────
        hod_user = await get_or_create(
            db, User, {"email": "hod.aids@ves.ac.in"},
            {
                "password_hash": get_password_hash("hod123"),
                "first_name": "Dr. Anjali",
                "last_name": "Sharma",
                "role": RoleEnum.hod,
                "is_active": True
            }
        )
        hod_profile = await get_or_create(
            db, FacultyProfile, {"user_id": hod_user.id},
            {
                "department_id": aids_dept.id,
                "designation": "HOD",
                "full_name": "Dr. Anjali Sharma"
            }
        )

        # ─── 6. Faculty Users ──────────────────────────────────────────────
        faculty_data = [
            {"email": "priya.mehta@ves.ac.in",   "first_name": "Dr. Priya",   "last_name": "Mehta",   "designation": "Assistant Professor"},
            {"email": "suresh.nair@ves.ac.in",   "first_name": "Mr. Suresh",  "last_name": "Nair",    "designation": "Assistant Professor"},
            {"email": "kavita.joshi@ves.ac.in",  "first_name": "Dr. Kavita",  "last_name": "Joshi",   "designation": "Associate Professor"},
        ]
        faculty_users = {}
        for fd in faculty_data:
            fu = await get_or_create(
                db, User, {"email": fd["email"]},
                {
                    "password_hash": get_password_hash("faculty123"),
                    "first_name": fd["first_name"],
                    "last_name": fd["last_name"],
                    "role": RoleEnum.faculty,
                    "is_active": True
                }
            )
            fp = await get_or_create(
                db, FacultyProfile, {"user_id": fu.id},
                {
                    "department_id": aids_dept.id,
                    "designation": fd["designation"],
                    "full_name": f"{fd['first_name']} {fd['last_name']}"
                }
            )
            faculty_users[fd["email"]] = (fu, fp)

        # ─── 7. Student Users ──────────────────────────────────────────────
        student_data = [
            {"email": "student.1@aids.ves.ac.in",  "first_name": "Rahul",   "last_name": "Verma",    "roll": "AIDS21001"},
            {"email": "student.2@aids.ves.ac.in",  "first_name": "Priya",   "last_name": "Singh",    "roll": "AIDS21002"},
            {"email": "student.3@aids.ves.ac.in",  "first_name": "Aditya",  "last_name": "Kumar",    "roll": "AIDS21003"},
            {"email": "student.4@aids.ves.ac.in",  "first_name": "Sneha",   "last_name": "Patel",    "roll": "AIDS21004"},
            {"email": "student.5@aids.ves.ac.in",  "first_name": "Rohan",   "last_name": "Shah",     "roll": "AIDS21005"},
            # Test/Demo student
            {"email": "puneetdhongade26@gmail.com","first_name": "Puneet",  "last_name": "Dhongade", "roll": "AIDS21099"},
        ]
        for sd in student_data:
            su = await get_or_create(
                db, User, {"email": sd["email"]},
                {
                    "password_hash": get_password_hash("student123"),
                    "first_name": sd["first_name"],
                    "last_name": sd["last_name"],
                    "role": RoleEnum.student,
                    "is_active": True
                }
            )
            sp = await get_or_create(
                db, StudentProfile, {"roll_number": sd["roll"]},
                {
                    "user_id": su.id,
                    "department_id": aids_dept.id,
                    "full_name": f"{sd['first_name']} {sd['last_name']}",
                    "admission_year": 2021
                }
            )

        # ─── 8. ClassSubject Mappings ──────────────────────────────────────
        # SE-A: ML, Data Warehousing taught by Dr. Priya Mehta
        priya_user, priya_profile = faculty_users["priya.mehta@ves.ac.in"]
        se_a = classes.get("SE-A")
        if se_a:
            for code in ["AIDS301", "AIDS302"]:
                await get_or_create(
                    db, ClassSubject,
                    {"class_id": se_a.id, "subject_id": subjects[code].id},
                    {"faculty_id": priya_profile.id}
                )
            # Python Lab by Suresh Nair
            suresh_user, suresh_profile = faculty_users["suresh.nair@ves.ac.in"]
            await get_or_create(
                db, ClassSubject,
                {"class_id": se_a.id, "subject_id": subjects["AIDS303"].id},
                {"faculty_id": suresh_profile.id}
            )

        # TE-A: Deep Learning, NLP by Dr. Kavita Joshi
        te_a = classes.get("TE-A")
        kavita_user, kavita_profile = faculty_users["kavita.joshi@ves.ac.in"]
        if te_a:
            for code in ["AIDS501", "AIDS502"]:
                await get_or_create(
                    db, ClassSubject,
                    {"class_id": te_a.id, "subject_id": subjects[code].id},
                    {"faculty_id": kavita_profile.id}
                )
            # Cloud Computing by HOD
            await get_or_create(
                db, ClassSubject,
                {"class_id": te_a.id, "subject_id": subjects["AIDS503"].id},
                {"faculty_id": hod_profile.id}
            )

        # ─── 9. Events ────────────────────────────────────────────────────
        today = date.today()
        event_data_list = [
            {"title": "Unit Test 1",                "description": "First unit test covering units 1 and 2",      "date": today + timedelta(days=2),  "department": "AIDS", "audience": "ALL"},
            {"title": "Assignment Submission",       "description": "Final submission for mini project phase 1",   "date": today + timedelta(days=4),  "department": "AIDS", "audience": "ALL"},
            {"title": "Guest Lecture — AI Industry","description": "Industry expert session on real-world AI",     "date": today + timedelta(days=7),  "department": "AIDS", "audience": "ALL"},
        ]
        for ed in event_data_list:
            await get_or_create(
                db, Event,
                {"title": ed["title"], "department": ed["department"]},
                {"description": ed["description"], "date": ed["date"], "audience": ed["audience"]}
            )

        await db.commit()
        logger.info("✅ Seed complete. All data is up to date.")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
