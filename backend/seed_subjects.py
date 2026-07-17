import asyncio
import sys
from sqlalchemy.future import select
from app.database import SessionLocal
from app.models import Subject

subjects_data = [
    # Semester I (FE)
    {"code": "NBS11", "name": "Fundamentals of Engineering Mathematics-1", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NBS13", "name": "Engineering Chemistry", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NBS14", "name": "Biology for Engineers", "department_id": "AIDS", "semester": 1, "year": "FE"},
    {"code": "NES14", "name": "Fundamentals of Programming (C/Java)", "department_id": "AIDS", "semester": 1, "year": "FE"},
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
    {"code": "NADPC32", "name": "Data Structure", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC33", "name": "Database Management System", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADPC34", "name": "Foundation of Data Science", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADMM31", "name": "Cryptography and System Security", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADAE31", "name": "Presentation & business communication", "department_id": "AIDS", "semester": 3, "year": "SE"},
    {"code": "NADEM31", "name": "Finance for Engineering", "department_id": "AIDS", "semester": 3, "year": "SE"},

    # Semester IV (SE)
    {"code": "NADPC41", "name": "Computer Network and Operating Systems", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADPC42", "name": "Analysis of Algorithms", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADPC43", "name": "Artificial Intelligence", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADMM41", "name": "Ethical Hacking and Digital Forensic", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NOE421", "name": "Open elective I", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADVS41", "name": "Mobile App Development", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADFP41", "name": "CEP Mobile App", "department_id": "AIDS", "semester": 4, "year": "SE"},
    {"code": "NADEM41", "name": "Innovation and Entrepreneurship", "department_id": "AIDS", "semester": 4, "year": "SE"},

    # Semester V (TE)
    {"code": "NADPC51", "name": "Machine Learning", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPC52", "name": "Data Mining", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPC53", "name": "Full Stack Development: Web Dev", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADPE51", "name": "PCE-I", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NADMM51", "name": "Blockchain - Application Development", "department_id": "AIDS", "semester": 5, "year": "TE"},
    {"code": "NOE501", "name": "Open elective II", "department_id": "AIDS", "semester": 5, "year": "TE"},

    # Semester VI (TE)
    {"code": "NADPC61", "name": "Deep Learning", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPC62", "name": "Generative AI", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADP61", "name": "Major Project - 1", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPE61", "name": "PEC-II", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADPE62", "name": "PEC-III", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADMM61", "name": "Secure Software Development", "department_id": "AIDS", "semester": 6, "year": "TE"},
    {"code": "NADVS61", "name": "AWS essential / Azure", "department_id": "AIDS", "semester": 6, "year": "TE"},

    # Semester VII (BE) - Custom
    {"code": "NBE701", "name": "Big Data Analytics", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBE702", "name": "Natural Language Processing", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBEE701", "name": "Elective IV", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBEE702", "name": "Elective V", "department_id": "AIDS", "semester": 7, "year": "BE"},
    {"code": "NBE799", "name": "Project Stage 1", "department_id": "AIDS", "semester": 7, "year": "BE"},

    # Semester VIII (BE) - Custom
    {"code": "NBE801", "name": "Reinforcement Learning", "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBE802", "name": "Computer Vision", "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBEE801", "name": "Elective VI", "department_id": "AIDS", "semester": 8, "year": "BE"},
    {"code": "NBE899", "name": "Project Stage 2", "department_id": "AIDS", "semester": 8, "year": "BE"},
]

async def seed_subjects():
    async with SessionLocal() as db:
        for sub_data in subjects_data:
            result = await db.execute(select(Subject).where(Subject.code == sub_data["code"]))
            existing = result.scalars().first()
            if not existing:
                new_sub = Subject(**sub_data)
                db.add(new_sub)
                print(f"Added subject: {new_sub.name}")
            else:
                existing.name = sub_data["name"]
                existing.department_id = sub_data["department_id"]
                existing.semester = sub_data["semester"]
                existing.year = sub_data["year"]
                print(f"Updated subject: {existing.name}")
        
        await db.commit()
        print("Subjects seeded successfully!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_subjects())
