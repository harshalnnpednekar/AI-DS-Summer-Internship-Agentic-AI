"""
Idempotent seed script for EduAgent Phase 2.

Creates all required demo data if it doesn't already exist:
- Departments (AIDS, CS)
- Academic Year (2025-2026, current)
- Classes (SE-A, SE-B, TE-A, BE-A)
- Subjects per semester (full VESIT subject list)
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
from app.auth import get_password_hash, verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Full VESIT subject list (all semesters) ──────────────────────────────────
subjects_data = [
    # Semester I (FE)
    {"code": "NBS11",   "name": "Fundamentals of Engineering Mathematics-1", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NBS13",   "name": "Engineering Chemistry",                      "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NBS14",   "name": "Biology for Engineers",                      "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NES14",   "name": "Fundamentals of Programming (Java)",         "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NPC11",   "name": "Programme Core Course",                      "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NIK11",   "name": "Fundamentals of Vedic Mathematics",          "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NVE11",   "name": "Universal Human Values-1",                   "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NVS11",   "name": "Basic Workshop Practice",                    "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NCC11",   "name": "Co curricular Course",                       "department_id": "AIDS", "semester": 1, "year": "FE"},

    # Semester II (FE)
    {"code": "NBS21",   "name": "Fundamentals of Engineering Mathematics-2",  "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NBS22",   "name": "Engineering Physics",                        "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NES21",   "name": "Engineering Mechanics",                      "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NES22",   "name": "Engineering Drawing",                        "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NES23",   "name": "Basic Electrical Engineering",               "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NAE21",   "name": "Professional Communications and Ethics-I",   "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NVE22",   "name": "Universal Human Values-2",                   "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NCC22",   "name": "Co curricular Course",                       "department_id": "AIDS", "semester": 2, "year": "FE"},

    # Semester III (SE)
    {"code": "NADPC31", "name": "Probability and Graph Theory",               "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC32", "name": "Data Structures",                            "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC33", "name": "Database Management System",                 "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC34", "name": "Foundation of Data Science",                 "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADMM31", "name": "Cryptography and System Security",           "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADAE31", "name": "Presentation & Business Communication",      "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADEM31", "name": "Finance for Engineering",                    "department_id": "AIDS", "semester": 3, "year": "SE"},

    # Semester IV (SE)
    {"code": "NADPC41", "name": "Computer Network and Operating Systems",     "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADPC42", "name": "Analysis of Algorithms",                     "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADPC43", "name": "Artificial Intelligence",                    "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADMM41", "name": "Ethical Hacking and Digital Forensics",      "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NOE421",  "name": "Open Elective I",                            "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADVS41", "name": "Mobile App Development",                     "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADFP41", "name": "CEP Mobile App",                             "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADEM41", "name": "Innovation and Entrepreneurship",            "department_id": "AIDS", "semester": 4, "year": "SE"},

    # Semester V (TE)
    {"code": "NADPC51", "name": "Machine Learning",                           "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPC52", "name": "Data Warehousing and Mining",                "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPC53", "name": "Full Stack Web Development",                 "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPE51", "name": "Program Elective Course - I",                "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADMM51", "name": "Blockchain - Application Development",       "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NOE501",  "name": "Open Elective II",                           "department_id": "AIDS", "semester": 5, "year": "TE"},

    # Semester VI (TE)
    {"code": "NADPC61", "name": "Deep Learning",                              "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPC62", "name": "Generative AI",                              "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADP61",  "name": "Major Project - 1",                          "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPE61", "name": "Program Elective Course - II",               "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPE62", "name": "Program Elective Course - III",              "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADMM61", "name": "Secure Software Development",                "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADVS61", "name": "AWS Essential / Azure",                      "department_id": "AIDS", "semester": 6, "year": "TE"},

    # Semester VII (BE)
    {"code": "NBE701",  "name": "Big Data Analytics",                         "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBE702",  "name": "Natural Language Processing",                "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBEE701", "name": "Program Elective Course - IV",               "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBEE702", "name": "Program Elective Course - V",                "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBE799",  "name": "Major Project - 2",                          "department_id": "AIDS", "semester": 7, "year": "BE"},

    # Semester VIII (BE)
    {"code": "NBE801",  "name": "Reinforcement Learning",                     "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBE802",  "name": "Computer Vision",                            "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBEE801", "name": "Program Elective Course - VI",               "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBE899",  "name": "Retrieval Augmented Generation",             "department_id": "AIDS", "semester": 8, "year": "BE"},
]


async def get_or_create(db, model, filters: dict, defaults: dict = None):  # type: ignore
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
        logger.info(f"Exists  {model.__name__}: {filters}")
    return obj


async def seed():
    """
    Seed demo users, departments, academic year, classes, subjects,
    class-subject mappings, and events.
    Run with: python -m app.seed
    """
    async with SessionLocal() as db:

        # ─── 1. Departments ───────────────────────────────────────────────
        aids_dept = await get_or_create(
            db, Department, {"code": "AIDS"},
            {"name": "Artificial Intelligence and Data Science"}
        )
        cs_dept = await get_or_create(
            db, Department, {"code": "CS"},
            {"name": "Computer Science"}
        )

        # ─── 2. Academic Year ─────────────────────────────────────────────
        ay = await get_or_create(
            db, AcademicYear, {"name": "2025-2026"},
            {
                "start_date": date(2025, 7, 1),
                "end_date":   date(2026, 6, 30),
                "is_current": True
            }
        )

        # ─── 3. Classes ───────────────────────────────────────────────────
        class_defs = [
            {"year_level": 2, "division": "A", "semester": 3},
            {"year_level": 2, "division": "B", "semester": 3},
            {"year_level": 3, "division": "A", "semester": 5},
            {"year_level": 4, "division": "A", "semester": 7},
        ]
        classes = {}
        for cd in class_defs:
            name = (
                "SE" if cd["year_level"] == 2 else
                "TE" if cd["year_level"] == 3 else
                "BE"
            ) + f"-{cd['division']}"
            c = await get_or_create(
                db, Class,
                {
                    "department_id":    aids_dept.id,
                    "academic_year_id": ay.id,
                    "year_level":       cd["year_level"],
                    "division":         cd["division"],
                    "semester":         cd["semester"],
                },
                {"name": name}
            )
            classes[name] = c

        # ─── 4. Subjects — full VESIT list (idempotent upsert) ───────────
        for sub_data in subjects_data:
            result = await db.execute(
                select(Subject).where(Subject.code == sub_data["code"])
            )
            existing = result.scalars().first()
            if not existing:
                new_sub = Subject(
                    code=sub_data["code"],
                    name=sub_data["name"],
                    year_level={"FE": 1, "SE": 2, "TE": 3, "BE": 4}[sub_data["year"]],
                    semester=sub_data["semester"],
                    department_id=str(aids_dept.id),
                    credits=sub_data.get("credits", 2),
                )
                db.add(new_sub)
                logger.info(f"Created Subject: {sub_data['code']}")
            else:
                existing.name       = sub_data["name"]
                existing.year_level = {"FE": 1, "SE": 2, "TE": 3, "BE": 4}[sub_data["year"]]  # type: ignore
                existing.semester   = sub_data["semester"]
                logger.info(f"Exists  Subject: {sub_data['code']}")
        await db.flush()

        # ─── 5. HOD User ──────────────────────────────────────────────────
        hod_user = await get_or_create(
            db, User, {"email": "hod.aids@ves.ac.in"},
            {
                "password_hash": get_password_hash("hod@123"),
                "first_name":    "HOD",
                "last_name":     "AIDS",
                "role":          RoleEnum.hod,
                "is_active":     True,
            }
        )
        if not verify_password("hod@123", hod_user.password_hash):
            hod_user.password_hash = get_password_hash("hod@123")
            logger.info("Reset HOD password to hod@123")

        hod_profile = await get_or_create(
            db, FacultyProfile, {"user_id": hod_user.id},
            {
                "department_id": aids_dept.id,
                "designation":   "HOD",
                "full_name":     "HOD AIDS",
            }
        )

        # ─── 6. Faculty Users ─────────────────────────────────────────────
        faculty_data = [
            {"email": "priya.mehta@ves.ac.in",  "first_name": "Dr. Priya",  "last_name": "Mehta",  "designation": "Assistant Professor", "password": "faculty@123"},
            {"email": "suresh.nair@ves.ac.in",  "first_name": "Mr. Suresh", "last_name": "Nair",   "designation": "Assistant Professor", "password": "faculty@123"},
            {"email": "kavita.joshi@ves.ac.in", "first_name": "Dr. Kavita", "last_name": "Joshi",  "designation": "Associate Professor", "password": "faculty@123"},
        ]
        faculty_users = {}
        for fd in faculty_data:
            fu = await get_or_create(
                db, User, {"email": fd["email"]},
                {
                    "password_hash": get_password_hash(fd["password"]),
                    "first_name":    fd["first_name"],
                    "last_name":     fd["last_name"],
                    "role":          RoleEnum.faculty,
                    "is_active":     True,
                }
            )
            if not verify_password(fd["password"], fu.password_hash):
                fu.password_hash = get_password_hash(fd["password"])
                logger.info(f"Reset {fd['email']} password")

            fp = await get_or_create(
                db, FacultyProfile, {"user_id": fu.id},
                {
                    "department_id": aids_dept.id,
                    "designation":   fd["designation"],
                    "full_name":     f"{fd['first_name']} {fd['last_name']}",
                }
            )
            faculty_users[fd["email"]] = (fu, fp)

        # ─── 7. Student Users ─────────────────────────────────────────────
        student_data = [
            {"email": "student1@ves.ac.in",         "first_name": "Test",   "last_name": "Student",  "roll": "AIDS21001", "password": "student@123"},
            {"email": "student.2@aids.ves.ac.in",   "first_name": "Priya",  "last_name": "Singh",    "roll": "AIDS21002", "password": "student@123"},
            {"email": "student.3@aids.ves.ac.in",   "first_name": "Aditya", "last_name": "Kumar",    "roll": "AIDS21003", "password": "student@123"},
            {"email": "student.4@aids.ves.ac.in",   "first_name": "Sneha",  "last_name": "Patel",    "roll": "AIDS21004", "password": "student@123"},
            {"email": "student.5@aids.ves.ac.in",   "first_name": "Rohan",  "last_name": "Shah",     "roll": "AIDS21005", "password": "student@123"},
            {"email": "puneetdhongade26@gmail.com", "first_name": "Puneet", "last_name": "Dhongade", "roll": "AIDS21099", "password": "student@123"},
        ]
        for sd in student_data:
            su = await get_or_create(
                db, User, {"email": sd["email"]},
                {
                    "password_hash": get_password_hash(sd["password"]),
                    "first_name":    sd["first_name"],
                    "last_name":     sd["last_name"],
                    "role":          RoleEnum.student,
                    "is_active":     True,
                }
            )
            if not verify_password(sd["password"], su.password_hash):
                su.password_hash = get_password_hash(sd["password"])
                logger.info(f"Reset {sd['email']} password")

            sp = await get_or_create(
                db, StudentProfile, {"roll_number": sd["roll"]},
                {
                    "user_id":          su.id,
                    "department_id":    aids_dept.id,
                    "full_name":        f"{sd['first_name']} {sd['last_name']}",
                    "admission_year":   2021,
                    "status":           "enrolled",
                }
            )

        # ─── 8. ClassSubject Mappings ─────────────────────────────────────
        priya_user,  priya_profile  = faculty_users["priya.mehta@ves.ac.in"]
        suresh_user, suresh_profile = faculty_users["suresh.nair@ves.ac.in"]
        kavita_user, kavita_profile = faculty_users["kavita.joshi@ves.ac.in"]

        async def fetch_subject(code):
            r = await db.execute(select(Subject).where(Subject.code == code))
            return r.scalars().first()

        s_ds = await fetch_subject("NADPC32")  # Data Structures (SE)
        s_ai = await fetch_subject("NADPC43")  # Artificial Intelligence (SE)
        s_ml = await fetch_subject("NADPC51")  # Machine Learning (TE)
        s_dl = await fetch_subject("NADPC61")  # Deep Learning (TE)

        se_a = classes.get("SE-A")
        te_a = classes.get("TE-A")

        if se_a and s_ds:
            await get_or_create(db, ClassSubject,
                {"class_id": se_a.id, "subject_id": s_ds.id},
                {"faculty_id": priya_profile.id})
        if se_a and s_ai:
            await get_or_create(db, ClassSubject,
                {"class_id": se_a.id, "subject_id": s_ai.id},
                {"faculty_id": priya_profile.id})
        if te_a and s_ml:
            await get_or_create(db, ClassSubject,
                {"class_id": te_a.id, "subject_id": s_ml.id},
                {"faculty_id": kavita_profile.id})
        if te_a and s_dl:
            await get_or_create(db, ClassSubject,
                {"class_id": te_a.id, "subject_id": s_dl.id},
                {"faculty_id": kavita_profile.id})

        # ─── 9. Events ────────────────────────────────────────────────────
        today = date.today()
        event_data_list = [
            {"title": "Unit Test 1",                 "description": "First unit test covering units 1 and 2",    "date": today + timedelta(days=2), "department": "AIDS", "audience": "ALL"},
            {"title": "Assignment Submission",        "description": "Final submission for mini project phase 1", "date": today + timedelta(days=4), "department": "AIDS", "audience": "ALL"},
            {"title": "Guest Lecture — AI Industry", "description": "Industry expert session on real-world AI",  "date": today + timedelta(days=7), "department": "AIDS", "audience": "ALL"},
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