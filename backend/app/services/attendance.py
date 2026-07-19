"""Attendance business logic — keeps route handlers thin."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Class,
    FacultyProfile,
    AttendanceSession,
    RoleEnum,
    StudentProfile,
    Subject,
    User,
)
from app.schemas import AcademicYearEnum, LectureAttendanceSubmit, SemesterEnum


def sort_classes(classes: list[Class]) -> list[Class]:
    def sort_key(c: Class) -> tuple[int, str]:
        prefix = c.name.split("-")[0]
        order = {"FE": 1, "SE": 2, "TE": 3, "BE": 4}
        return (order.get(prefix, 99), c.name)  # type: ignore

    return sorted(classes, key=sort_key)


async def get_form_meta(db: AsyncSession) -> dict[str, Any]:
    classes_result = await db.execute(select(Class))
    subjects_result = await db.execute(select(Subject).order_by(Subject.name))
    classes = sort_classes(list(classes_result.scalars().all()))
    subjects = subjects_result.scalars().all()

    return {
        "classes": [
            {"id": str(c.id), "name": c.name, "total_students": c.total_students}
            for c in classes
        ],
        "subjects": [
            {"id": str(s.id), "code": s.code, "name": s.name} for s in subjects
        ],
        "academic_years": [year.value for year in AcademicYearEnum],
        "semesters": [sem.value for sem in SemesterEnum],
    }


async def submit_lecture_attendance(
    db: AsyncSession,
    faculty: User,
    payload: LectureAttendanceSubmit,
) -> tuple[bool, dict[str, Any] | None, str | None]:
    if payload.students_present_count > payload.total_students_enrolled:
        return False, None, "Present count cannot exceed total enrolled."

    if not payload.academic_year or not payload.semester:
        return False, None, "Academic year and semester are required."

    record = AttendanceSession(
        faculty_id=faculty.id,
        class_id=payload.class_id,
        subject_id=payload.subject_id,
        session_date=payload.lecture_date,
        time_slot=payload.time_slot,
        topic_covered=payload.topic_covered,
        total_students_enrolled=payload.total_students_enrolled,
        students_present_count=payload.students_present_count,
        absentee_roll_numbers=payload.absentee_roll_numbers or [],
        session_type=payload.session_type,
        academic_year=payload.academic_year.value,
        semester=payload.semester.value,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return True, {"id": str(record.id), "message": "Attendance submitted successfully."}, None


async def _get_hod_department(db: AsyncSession, user: User) -> str | None:
    result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == user.id)
    )
    profile = result.scalars().first()
    return profile.department if profile else None


async def _fetch_lectures(
    db: AsyncSession,
    user: User,
    hod_dept: str | None,
) -> list[tuple[AttendanceSession, str, str, str, str]]:
    query = (
        select(
            AttendanceSession,
            Class.name,
            Subject.name,
            User.first_name,
            User.last_name,
        )
        .join(Class, AttendanceSession.class_id == Class.id)
        .join(Subject, AttendanceSession.subject_id == Subject.id)
        .join(User, AttendanceSession.faculty_id == User.id)
    )

    if user.role == RoleEnum.hod:  # type: ignore
        if hod_dept:
            query = query.where(Class.department_id == hod_dept)
    else:
        query = query.where(AttendanceSession.faculty_id == user.id)

    result = await db.execute(query)
    return list(result.all())  # type: ignore


async def _get_class_roll_numbers(
    db: AsyncSession, class_name: str
) -> list[str]:
    result = await db.execute(
        select(StudentProfile.roll_number)
        .where(StudentProfile.division == class_name)
        .order_by(StudentProfile.roll_number)
    )
    return [r for r in result.scalars().all()]


def _normalize_session_type(session_type: str | None) -> str:
    if session_type in ("Lecture", "Theory"):
        return "Theory"
    if session_type in ("Lab", "Practical"):
        return "Practical"
    return session_type or "Theory"


async def get_attendance_stats(
    db: AsyncSession, user: User
) -> dict[str, Any]:
    hod_dept = await _get_hod_department(db, user) if user.role == RoleEnum.hod else None  # type: ignore
    all_lectures = await _fetch_lectures(db, user, hod_dept)

    total_lectures = len(all_lectures)
    total_enrolled = sum(row[0].total_students_enrolled for row in all_lectures)
    total_present = sum(row[0].students_present_count for row in all_lectures)
    avg_attendance = (
        round((total_present / total_enrolled) * 100) if total_enrolled > 0 else 0  # type: ignore
    )

    class_wise_dict: dict[str, dict[str, Any]] = {}
    for lecture, class_name, subject_name, first_name, last_name in all_lectures:
        key = f"{class_name}_{subject_name}_{lecture.session_type}"
        if key not in class_wise_dict:
            class_wise_dict[key] = {
                "class": class_name,
                "subject": subject_name,
                "session_type": lecture.session_type,
                "professor": f"{first_name} {last_name}",
                "lectures": 0,
                "total_enrolled": 0,
                "total_present": 0,
            }
        class_wise_dict[key]["lectures"] += 1
        class_wise_dict[key]["total_enrolled"] += lecture.total_students_enrolled
        class_wise_dict[key]["total_present"] += lecture.students_present_count

    class_wise_stats = []
    under_75_count = 0
    for stats in class_wise_dict.values():
        att_pct = (
            round((stats["total_present"] / stats["total_enrolled"]) * 100)
            if stats["total_enrolled"] > 0
            else 0
        )
        stats["attendance"] = f"{att_pct}%"
        stats["attendance_num"] = att_pct
        if att_pct < 75:
            under_75_count += 1
        class_wise_stats.append(stats)

    recent_query = (
        select(AttendanceSession, Class.name, Subject.name)
        .join(Class, AttendanceSession.class_id == Class.id)
        .join(Subject, AttendanceSession.subject_id == Subject.id)
    )
    if user.role == RoleEnum.hod:  # type: ignore
        if hod_dept:
            recent_query = recent_query.where(Class.department_id == hod_dept)
    else:
        recent_query = recent_query.where(
            AttendanceSession.faculty_id == user.id
        )
    recent_query = recent_query.order_by(AttendanceSession.created_at.desc())
    recent_result = await db.execute(recent_query)
    recent_list = recent_result.all()

    recent_lectures = []
    for lecture, class_name, subject_name in recent_list:
        absentees = [str(r) for r in (lecture.absentee_roll_numbers or [])]
        enrolled_rolls = await _get_class_roll_numbers(db, class_name)
        if enrolled_rolls:
            present_rolls = [r for r in enrolled_rolls if r not in absentees]
        else:
            present_rolls = []

        recent_lectures.append(
            {
                "id": str(lecture.id),
                "class_name": class_name,
                "subject_name": subject_name,
                "session_type": lecture.session_type,
                "date": lecture.session_date.strftime("%b %d, %Y"),
                "time_slot": lecture.time_slot,
                "topic": lecture.topic_covered,
                "present": lecture.students_present_count,
                "total": lecture.total_students_enrolled,
                "absentees": absentees,
                "present_roll_numbers": present_rolls,
            }
        )

    return {
        "total_lectures": total_lectures,
        "avg_attendance": avg_attendance,
        "under_75_count": under_75_count,
        "class_wise_stats": class_wise_stats,
        "recent_lectures": recent_lectures,
    }


async def get_defaulters(db: AsyncSession) -> list[dict[str, Any]]:
    lectures_query = await db.execute(
        select(AttendanceSession, Class.name, Subject.name)
        .join(Class, AttendanceSession.class_id == Class.id)
        .join(Subject, AttendanceSession.subject_id == Subject.id)
        .order_by(Class.name, Subject.name, AttendanceSession.session_date)
    )
    lectures = lectures_query.all()
    if not lectures:
        return []

    class_data: dict[str, dict[str, Any]] = {}
    for lecture, class_name, subject_name in lectures:
        key = f"{class_name} - {subject_name}"
        if key not in class_data:
            class_data[key] = {
                "total_theory": 0,
                "total_practical": 0,
                "absentees": {},
                "class_name": class_name,
                "subject_name": subject_name,
            }

        session_type = _normalize_session_type(lecture.session_type)
        if session_type == "Theory":
            class_data[key]["total_theory"] += 1
        else:
            class_data[key]["total_practical"] += 1

        for roll in lecture.absentee_roll_numbers or []:
            roll = str(roll).strip()
            if not roll:
                continue
            if roll not in class_data[key]["absentees"]:
                class_data[key]["absentees"][roll] = {"Theory": 0, "Practical": 0}
            class_data[key]["absentees"][roll][session_type] += 1

    profiles_query = await db.execute(
        select(StudentProfile, User).join(User, StudentProfile.user_id == User.id)
    )
    roll_to_name = {
        sp.roll_number: f"{u.first_name} {u.last_name}"
        for sp, u in profiles_query.all()
    }

    defaulter_list = []
    for key, data in class_data.items():
        total_t = data["total_theory"]
        total_p = data["total_practical"]
        if total_t == 0 and total_p == 0:
            continue

        for roll, absent_counts in data["absentees"].items():
            absent_t = absent_counts["Theory"]
            absent_p = absent_counts["Practical"]

            theory_pct = (
                round(((total_t - absent_t) / total_t) * 100) if total_t > 0 else "N/A"
            )
            practical_pct = (
                round(((total_p - absent_p) / total_p) * 100) if total_p > 0 else "N/A"
            )

            total_sessions = total_t + total_p
            total_attended = (total_t - absent_t) + (total_p - absent_p)
            attendance_pct = (
                round((total_attended / total_sessions) * 100)
                if total_sessions > 0
                else "N/A"
            )

            if isinstance(attendance_pct, int) and attendance_pct < 75:
                status = "Critical" if attendance_pct < 50 else "At Risk"
                defaulter_list.append(
                    {
                        "id": f"{roll}-{data['subject_name']}",
                        "roll": roll,
                        "name": roll_to_name.get(roll, roll),
                        "class": key,
                        "original_class": data["class_name"],
                        "subject": data["subject_name"],
                        "theory_attendance": theory_pct,
                        "practical_attendance": practical_pct,
                        "attendance": attendance_pct,
                        "status": status,
                        "checked": False,
                    }
                )

    defaulter_list.sort(
        key=lambda x: (0 if x["status"] == "Critical" else 1, x["attendance"])
    )
    return defaulter_list
