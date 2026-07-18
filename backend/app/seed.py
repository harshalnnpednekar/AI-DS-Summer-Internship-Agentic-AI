import asyncio
import sys
import uuid
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import User, RoleEnum, Class, Subject, FacultySubjectMapping, FacultyProfile

subjects_data = [
    # Semester I (FE)
    {"code": "NBS11", "name": "Fundamentals of Engineering Mathematics-1", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NBS13", "name": "Engineering Chemistry", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NBS14", "name": "Biology for Engineers", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NES14", "name": "Fundamentals of Programming (Java)", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NPC11", "name": "Programme Core Course", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NIK11", "name": "Fundamentals of Vedic Mathematics", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NVE11", "name": "Universal Human Values-1", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NVS11", "name": "Basic Workshop Practice", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NCC11", "name": "Co curricular Course", "department_id": "AIDS", "semester": 1, "year": "FE"},

    # Semester II (FE)
    {"code": "NBS21", "name": "Fundamentals of Engineering Mathematics-2", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NBS22", "name": "Engineering Physics", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NES21", "name": "Engineering Mechanics", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NES22", "name": "Engineering Drawing", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NES23", "name": "Basic Electrical Engineering", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NAE21", "name": "Professional Communications and Ethics-I", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NVE22", "name": "Universal Human Values-2", "department_id": "AIDS", "semester": 2, "year": "FE"},
    {"code": "NCC22", "name": "Co curricular Course", "department_id": "AIDS", "semester": 2, "year": "FE"},

    # Semester III (SE)
    {"code": "NADPC31", "name": "Probability and Graph Theory", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC32", "name": "Data Structures", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC33", "name": "Database Management System", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC34", "name": "Foundation of Data Science", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADMM31", "name": "Cryptography and System Security", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADAE31", "name": "Presentation & Business Communication", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADEM31", "name": "Finance for Engineering", "department_id": "AIDS", "semester": 3, "year": "SE"},

    # Semester IV (SE)
    {"code": "NADPC41", "name": "Computer Network and Operating Systems", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADPC42", "name": "Analysis of Algorithms", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADPC43", "name": "Artificial Intelligence", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADMM41", "name": "Ethical Hacking and Digital Forensics", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NOE421", "name": "Open Elective I", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADVS41", "name": "Mobile App Development", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADFP41", "name": "CEP Mobile App", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADEM41", "name": "Innovation and Entrepreneurship", "department_id": "AIDS", "semester": 4, "year": "SE"},

    # Semester V (TE)
    {"code": "NADPC51", "name": "Machine Learning", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPC52", "name": "Data Warehousing and Mining", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPC53", "name": "Full Stack Web Development", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPE51", "name": "Program Elective Course - I", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADMM51", "name": "Blockchain - Application Development", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NOE501", "name": "Open Elective II", "department_id": "AIDS", "semester": 5, "year": "TE"},

    # Semester VI (TE)
    {"code": "NADPC61", "name": "Deep Learning", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPC62", "name": "Generative AI", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADP61", "name": "Major Project - 1", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPE61", "name": "Program Elective Course - II", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPE62", "name": "Program Elective Course - III", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADMM61", "name": "Secure Software Development", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADVS61", "name": "AWS Essential / Azure", "department_id": "AIDS", "semester": 6, "year": "TE"},

    # Semester VII (BE) - Custom
    {"code": "NBE701", "name": "Big Data Analytics", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBE702", "name": "Natural Language Processing", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBEE701", "name": "Program Elective Course - IV", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBEE702", "name": "Program Elective Course - V", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBE799", "name": "Major Project - 2", "department_id": "AIDS", "semester": 7, "year": "BE"},

    # Semester VIII (BE) - Custom
    {"code": "NBE801", "name": "Reinforcement Learning", "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBE802", "name": "Computer Vision", "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBEE801", "name": "Program Elective Course - VI", "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBE899", "name": "Retrieval Augmented Generation", "department_id": "AIDS", "semester": 8, "year": "BE"},
]

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
        if hod and faculty:
            # Check and Create Classes
            c1_res = await db.execute(select(Class).where(Class.name == "SE-A"))
            c1 = c1_res.scalars().first()
            if not c1:
                c1 = Class(name="SE-A", department_id="AIDS", total_students=60)
                db.add(c1)
            
            c2_res = await db.execute(select(Class).where(Class.name == "TE-A"))
            c2 = c2_res.scalars().first()
            if not c2:
                c2 = Class(name="TE-A", department_id="AIDS", total_students=65)
                db.add(c2)
            await db.flush()

            # Check and Create Subjects (All 56 Subjects)
            for sub_data in subjects_data:
                result = await db.execute(select(Subject).where(Subject.code == sub_data["code"]))
                existing = result.scalars().first()
                if not existing:
                    new_sub = Subject(**sub_data)
                    db.add(new_sub)
                else:
                    existing.name = sub_data["name"]
                    existing.department_id = sub_data["department_id"]
                    existing.semester = sub_data["semester"]
                    existing.year = sub_data["year"]
            
            await db.flush()

            # For mapping, we need to specifically fetch DS101 and AI101 to map them to Priya Mehta's classes
            s1_res = await db.execute(select(Subject).where(Subject.code == "NADPC32")) # DS Data Structure
            s1 = s1_res.scalars().first()
            s2_res = await db.execute(select(Subject).where(Subject.code == "NADPC43")) # AI
            s2 = s2_res.scalars().first()

            if s1 and s2:
                # Check and Create Mappings for Faculty (Dr. Priya Mehta)
                m1_res = await db.execute(select(FacultySubjectMapping).where(FacultySubjectMapping.faculty_id == faculty.id, FacultySubjectMapping.class_id == c1.id, FacultySubjectMapping.subject_id == s1.id))
                if not m1_res.scalars().first():
                    m1 = FacultySubjectMapping(faculty_id=faculty.id, class_id=c1.id, subject_id=s1.id)
                    db.add(m1)
                    
                m2_res = await db.execute(select(FacultySubjectMapping).where(FacultySubjectMapping.faculty_id == faculty.id, FacultySubjectMapping.class_id == c2.id, FacultySubjectMapping.subject_id == s2.id))
                if not m2_res.scalars().first():
                    m2 = FacultySubjectMapping(faculty_id=faculty.id, class_id=c2.id, subject_id=s2.id)
                    db.add(m2)
        
        await db.commit()
        print("Classes, Subjects, and Mappings seeded successfully!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_attendance_data())
