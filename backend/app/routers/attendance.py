from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from ..database import get_db
from ..models import User, RoleEnum, Class, Subject, FacultySubjectMapping, LectureAttendance, FacultyProfile
from ..dependencies import get_current_active_user, RoleChecker
from ..schemas_omnisync import StandardResponse, LectureAttendanceSubmit

router = APIRouter(
    prefix="/api/attendance",
    tags=["OmniSync Attendance"],
)

allow_faculty_hod = RoleChecker([RoleEnum.FACULTY, RoleEnum.HOD])

@router.get("/form-meta", response_model=StandardResponse)
async def get_form_meta(
    current_user: User = Depends(allow_faculty_hod),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role in [RoleEnum.HOD, RoleEnum.FACULTY]:
        # User requested all faculties to see all classes in dropdowns
        classes_result = await db.execute(select(Class))
        subjects_result = await db.execute(select(Subject).order_by(Subject.name))
        classes = classes_result.scalars().all()
        subjects = subjects_result.scalars().all()
        
        # Sort classes by academic year sequence (FE, SE, TE, BE)
        def sort_class(c):
            prefix = c.name.split('-')[0]
            order = {"FE": 1, "SE": 2, "TE": 3, "BE": 4}
            return (order.get(prefix, 99), c.name)
            
        classes = sorted(classes, key=sort_class)
        return StandardResponse(
            success=True,
            data={
                "classes": [{"id": str(c.id), "name": c.name, "total_students": c.total_students} for c in classes],
                "subjects": [{"id": str(s.id), "code": s.code, "name": s.name} for s in subjects]
            }
        )

@router.post("/submit", response_model=StandardResponse)
async def submit_attendance(
    attendance: LectureAttendanceSubmit, 
    current_user: User = Depends(allow_faculty_hod), 
    db: AsyncSession = Depends(get_db)
):
    # Validation
    if attendance.students_present_count > attendance.total_students_enrolled:
         return StandardResponse(success=False, error="Present count cannot exceed total enrolled.", data=None)
         
    # Security check bypassed as per user request to allow all faculties 
    # to select and submit attendance for all classes/subjects.

    # Updates can only be executed via HOD administrative override tools. (Immutability enforced by lack of PUT/PATCH)
    new_attendance = LectureAttendance(
        faculty_id=current_user.id,
        class_id=attendance.class_id,
        subject_id=attendance.subject_id,
        lecture_date=attendance.lecture_date,
        topic_covered=attendance.topic_covered,
        total_students_enrolled=attendance.total_students_enrolled,
        students_present_count=attendance.students_present_count,
        absentee_roll_numbers=attendance.absentee_roll_numbers,
        session_type=attendance.session_type
    )
    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)
    
    return StandardResponse(
        success=True,
        data={"id": str(new_attendance.id), "message": "Attendance submitted successfully."},
        error=None
    )

@router.get("/stats", response_model=StandardResponse)
async def get_attendance_stats(
    current_user: User = Depends(allow_faculty_hod),
    db: AsyncSession = Depends(get_db)
):
    hod_dept = None
    if current_user.role == RoleEnum.HOD:
        hod_profile_result = await db.execute(
            select(FacultyProfile).where(FacultyProfile.user_id == current_user.id)
        )
        hod_profile = hod_profile_result.scalars().first()
        hod_dept = hod_profile.department if hod_profile else None

    if current_user.role == RoleEnum.HOD:
        print(f"DEBUG: HOD role detected! hod_dept is: {hod_dept}")
        query = (
            select(LectureAttendance, Class.name, Subject.name, User.first_name, User.last_name)
            .join(Class, LectureAttendance.class_id == Class.id)
            .join(Subject, LectureAttendance.subject_id == Subject.id)
            .join(User, LectureAttendance.faculty_id == User.id)
        )
        if hod_dept:
            query = query.where(Class.department_id == hod_dept)
        # No filter → HOD sees all lectures across all departments
        all_lectures_result = await db.execute(query)
        all_lectures_list = all_lectures_result.all()
        print(f"DEBUG: all_lectures length for HOD is {len(all_lectures_list)}")
        # We need to recreate the iterator or just use the list
        all_lectures = all_lectures_list
    else:
        all_lectures_result = await db.execute(
            select(LectureAttendance, Class.name, Subject.name, User.first_name, User.last_name)
            .join(Class, LectureAttendance.class_id == Class.id)
            .join(Subject, LectureAttendance.subject_id == Subject.id)
            .join(User, LectureAttendance.faculty_id == User.id)
            .where(LectureAttendance.faculty_id == current_user.id)
        )
        all_lectures = all_lectures_result.all()
    
    total_lectures = len(all_lectures)
    total_enrolled = sum(l[0].total_students_enrolled for l in all_lectures)
    total_present = sum(l[0].students_present_count for l in all_lectures)
    
    avg_attendance = 0
    if total_enrolled > 0:
        avg_attendance = round((total_present / total_enrolled) * 100)
        
    class_wise_dict = {}
    for l, c_name, s_name, f_fname, f_lname in all_lectures:
        key = f"{c_name}_{s_name}_{l.session_type}"
        if key not in class_wise_dict:
            class_wise_dict[key] = {
                "class": c_name,
                "subject": s_name,
                "session_type": l.session_type,
                "professor": f"{f_fname} {f_lname}",
                "lectures": 0,
                "total_enrolled": 0,
                "total_present": 0
            }
        class_wise_dict[key]["lectures"] += 1
        class_wise_dict[key]["total_enrolled"] += l.total_students_enrolled
        class_wise_dict[key]["total_present"] += l.students_present_count
        
    class_wise_stats = []
    under_75_count = 0
    for stats in class_wise_dict.values():
        att_pct = round((stats["total_present"] / stats["total_enrolled"]) * 100) if stats["total_enrolled"] > 0 else 0
        stats["attendance"] = f"{att_pct}%"
        stats["attendance_num"] = att_pct
        if att_pct < 75:
            under_75_count += 1
        class_wise_stats.append(stats)
        
    # Fetch recent 5 lectures for activity feed
    if current_user.role == RoleEnum.HOD:
        query = (
            select(LectureAttendance, Class.name, Subject.name)
            .join(Class, LectureAttendance.class_id == Class.id)
            .join(Subject, LectureAttendance.subject_id == Subject.id)
        )
        if hod_dept:
            query = query.where(Class.department_id == hod_dept)
        # No filter → HOD sees all recent lectures
        query = query.order_by(LectureAttendance.created_at.desc()).limit(5)
        recent_result = await db.execute(query)
    else:
        recent_result = await db.execute(
            select(LectureAttendance, Class.name, Subject.name)
            .join(Class, LectureAttendance.class_id == Class.id)
            .join(Subject, LectureAttendance.subject_id == Subject.id)
            .where(LectureAttendance.faculty_id == current_user.id)
            .order_by(LectureAttendance.created_at.desc())
            .limit(5)
        )
        
    recent_list = recent_result.all()
    recent_lectures = []
    for l, c_name, s_name in recent_list:
        recent_lectures.append({
            "id": str(l.id),
            "class_name": c_name,
            "subject_name": s_name,
            "session_type": l.session_type,
            "date": l.lecture_date.strftime("%b %d, %Y"),
            "topic": l.topic_covered,
            "present": l.students_present_count,
            "total": l.total_students_enrolled,
            "absentees": l.absentee_roll_numbers or []
        })
        
    return StandardResponse(
        success=True,
        data={
            "total_lectures": total_lectures,
            "avg_attendance": avg_attendance,
            "under_75_count": under_75_count,
            "class_wise_stats": class_wise_stats,
            "recent_lectures": recent_lectures
        },
        error=None
    )
