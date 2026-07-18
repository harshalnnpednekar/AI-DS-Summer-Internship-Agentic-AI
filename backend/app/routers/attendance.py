from app.models import DefaulterList
from app.schemas import DefaulterListResponse
from app.models import StudentProfile
from requests import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from ..database import get_db
from ..models import User, RoleEnum, Class, Subject, FacultySubjectMapping, LectureAttendance, FacultyProfile
from ..dependencies import get_current_active_user, RoleChecker
from ..schemas import StandardResponse, LectureAttendanceSubmit
from app.services.excel_agent.excel_sync import excel_sync_agent
from fastapi.responses import FileResponse, Response
import os

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
        mappings_result = await db.execute(select(FacultySubjectMapping).where(FacultySubjectMapping.faculty_id == current_user.id))
        classes = classes_result.scalars().all()
        subjects = subjects_result.scalars().all()
        mappings = mappings_result.scalars().all()
        
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
                "subjects": [{"id": str(s.id), "code": s.code, "name": s.name, "year": s.year, "semester": s.semester} for s in subjects],
                "mappings": [{"class_id": str(m.class_id), "subject_id": str(m.subject_id)} for m in mappings]
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
        time_slot=attendance.time_slot,
        topic_covered=attendance.topic_covered,
        total_students_enrolled=attendance.total_students_enrolled,
        students_present_count=attendance.students_present_count,
        absentee_roll_numbers=attendance.absentee_roll_numbers,
        session_type=attendance.session_type
    )
    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)

    # Fetch additional data for Excel sync
    class_res = await db.execute(select(Class).where(Class.id == attendance.class_id))
    class_obj = class_res.scalars().first()
    
    subject_res = await db.execute(select(Subject).where(Subject.id == attendance.subject_id))
    subject_obj = subject_res.scalars().first()
    
    faculty_name = f"{current_user.first_name} {current_user.last_name}"

    # Normalize session_type
    raw_session_type = attendance.session_type or "Theory"
    if raw_session_type in ("Lecture", "lecture"): normalized_session_type = "Theory"
    elif raw_session_type in ("Lab", "lab"): normalized_session_type = "Practical"
    else: normalized_session_type = raw_session_type

    # Build name_lookup dict from all student profiles (roll_number -> name)
    all_sp_res = await db.execute(
        select(StudentProfile, User).join(User, StudentProfile.user_id == User.id)
    )
    name_lookup = {
        str(sp.roll_number): f"{u.first_name} {u.last_name}"
        for sp, u in all_sp_res.all()
    }

    # We no longer generate the Excel sheet synchronously here.
    # It is generated on-the-fly when requested via the /excel/subject endpoint.
    
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
        query = query.order_by(LectureAttendance.created_at.desc())
        recent_result = await db.execute(query)
    else:
        recent_result = await db.execute(
            select(LectureAttendance, Class.name, Subject.name)
            .join(Class, LectureAttendance.class_id == Class.id)
            .join(Subject, LectureAttendance.subject_id == Subject.id)
            .where(LectureAttendance.faculty_id == current_user.id)
            .order_by(LectureAttendance.created_at.desc())
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
            "time_slot": l.time_slot,
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

@router.get("/defaulters", response_model=StandardResponse)
async def get_defaulters(
    current_user: User = Depends(allow_faculty_hod),
    db: AsyncSession = Depends(get_db)
):
    """
    Compute defaulters from actual lecture attendance records.
    
    For each class, we look at every lecture conducted.
    A student (identified by roll number) is absent from a lecture if their
    roll number appears in `absentee_roll_numbers`.
    
    Attendance % = (Lectures NOT absent / Total lectures in that class) * 100
    - Below 75%: At Risk (defaulter)
    - Below 50%: Critical
    """
    # Fetch all lectures with their class name and subject name
    query = (
        select(LectureAttendance, Class.name, Subject.name)
        .join(Class, LectureAttendance.class_id == Class.id)
        .join(Subject, LectureAttendance.subject_id == Subject.id)
    )
    
    if getattr(current_user.role, 'value', current_user.role) == "FACULTY" or getattr(current_user.role, 'name', '') == "FACULTY" or current_user.role == RoleEnum.FACULTY:
        query = query.where(LectureAttendance.faculty_id == current_user.id)
        
    query = query.order_by(Class.name, Subject.name, LectureAttendance.lecture_date)
    
    lectures_query = await db.execute(query)
    lectures = lectures_query.all()

    if not lectures:
        return StandardResponse(success=True, data=[], error=None)

    # Build per-class-subject structure:
    class_data: dict = {}

    for lecture, class_name, subject_name in lectures:
        key = f"{class_name} - {subject_name}"
        if key not in class_data:
            class_data[key] = {
                "total_theory": 0,
                "total_practical": 0,
                "absentees": {},
                "class_name": class_name,
                "subject_name": subject_name
            }
            
        session_type = lecture.session_type or "Theory"
        if session_type == "Lecture":
            session_type = "Theory"
            
        if session_type == "Theory":
            class_data[key]["total_theory"] += 1
        elif session_type == "Practical":
            class_data[key]["total_practical"] += 1
        else:
            # Fallback if there's any other strange session type
            class_data[key]["total_theory"] += 1
            session_type = "Theory"

        absentees = lecture.absentee_roll_numbers or []
        for roll in absentees:
            roll = str(roll).strip()
            if roll:
                if roll not in class_data[key]["absentees"]:
                    class_data[key]["absentees"][roll] = {"Theory": 0, "Practical": 0}
                
                class_data[key]["absentees"][roll][session_type] += 1

    # Fetch all student profiles for name lookup (roll_number -> name)
    profiles_query = await db.execute(
        select(StudentProfile, User).join(User, StudentProfile.user_id == User.id)
    )
    profiles = profiles_query.all()
    roll_to_name: dict = {
        sp.roll_number: f"{u.first_name} {u.last_name}"
        for sp, u in profiles
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
            
            theory_pct = round(((total_t - absent_t) / total_t) * 100) if total_t > 0 else "N/A"
            practical_pct = round(((total_p - absent_p) / total_p) * 100) if total_p > 0 else "N/A"
            
            total_sessions = total_t + total_p
            total_attended = (total_t - absent_t) + (total_p - absent_p)
            attendance_pct = round((total_attended / total_sessions) * 100) if total_sessions > 0 else "N/A"

            if attendance_pct < 75:
                status = "Critical" if attendance_pct < 50 else "At Risk"
                defaulter_list.append({
                    "id": f"{roll}-{data['subject_name']}", # Make unique since same student could be in multiple subjects
                    "roll": roll,
                    "name": roll_to_name.get(roll, roll),   # fallback to roll number if not in profiles
                    "class": key, # Grouping key for frontend
                    "original_class": data["class_name"],
                    "subject": data["subject_name"],
                    "theory_attendance": theory_pct,
                    "practical_attendance": practical_pct,
                    "attendance": attendance_pct,
                    "status": status,
                    "checked": False
                })

    # Sort: Critical first, then by attendance ascending
    defaulter_list.sort(key=lambda x: (0 if x["status"] == "Critical" else 1, x["attendance"]))

    return StandardResponse(
        success=True,
        data=defaulter_list,
        error=None
    )

from pydantic import BaseModel
class BroadcastRequest(BaseModel):
    defaulter_ids: List[str]

@router.post("/defaulters/broadcast", response_model=StandardResponse)
async def broadcast_defaulters(
    payload: BroadcastRequest,
    current_user: User = Depends(allow_faculty_hod)
):
    print(f"Simulating broadcasting emails to class for {len(payload.defaulter_ids)} students.")
    return StandardResponse(success=True, data="Emails successfully broadcasted to the entire class as per service.", error=None)



allow_student = RoleChecker([RoleEnum.STUDENT])

@router.get("/student/me", response_model=StandardResponse)
async def get_my_attendance(
    current_user: User = Depends(allow_student),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns per-subject attendance stats for the currently logged-in student.
    Matches by roll_number in absentee_roll_numbers and student's division.
    """
    # Fetch student profile
    sp_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    student_profile = sp_result.scalars().first()
    if not student_profile:
        return StandardResponse(success=False, data=None, error="Student profile not found.")

    roll = str(student_profile.roll_number)
    division = student_profile.division

    # Fetch all lectures for this student's class division
    lectures_result = await db.execute(
        select(LectureAttendance, Class.name, Subject.name, Subject.code, User.first_name, User.last_name)
        .join(Class, LectureAttendance.class_id == Class.id)
        .join(Subject, LectureAttendance.subject_id == Subject.id)
        .join(User, LectureAttendance.faculty_id == User.id)
        .where(Class.name == division)
        .order_by(Subject.name, LectureAttendance.lecture_date)
    )
    lectures = lectures_result.all()

    if not lectures:
        return StandardResponse(success=True, data={
            "roll_number": roll,
            "division": division,
            "overall_attendance": 0,
            "total_theory": 0,
            "total_practical": 0,
            "attended_theory": 0,
            "attended_practical": 0,
            "subject_wise": [],
            "recent_lectures": [],
            "is_defaulter": False,
            "defaulter_status": None
        }, error=None)

    # Build per-subject stats
    subject_map = {}
    for lecture, class_name, subject_name, subject_code, f_first, f_last in lectures:
        key = f"{subject_name}_{lecture.session_type or 'Theory'}"
        # Normalize session type
        raw_st = lecture.session_type or "Theory"
        if raw_st in ("Lecture", "lecture"): raw_st = "Theory"
        elif raw_st in ("Lab", "lab"): raw_st = "Practical"

        subject_key = subject_name
        if subject_key not in subject_map:
            subject_map[subject_key] = {
                "subject": subject_name,
                "code": subject_code,
                "faculty": f"{f_first} {f_last}",
                "total_theory": 0,
                "total_practical": 0,
                "absent_theory": 0,
                "absent_practical": 0,
            }

        absentees = [str(r).strip() for r in (lecture.absentee_roll_numbers or [])]
        is_absent = roll in absentees

        if raw_st == "Theory":
            subject_map[subject_key]["total_theory"] += 1
            if is_absent:
                subject_map[subject_key]["absent_theory"] += 1
        else:
            subject_map[subject_key]["total_practical"] += 1
            if is_absent:
                subject_map[subject_key]["absent_practical"] += 1

    # Compute attendance percentages per subject
    subject_wise = []
    grand_total = 0
    grand_attended = 0

    for subj, d in subject_map.items():
        tot_t = d["total_theory"]
        tot_p = d["total_practical"]
        att_t = tot_t - d["absent_theory"]
        att_p = tot_p - d["absent_practical"]
        total = tot_t + tot_p
        attended = att_t + att_p
        pct = round((attended / total) * 100) if total > 0 else 0
        theory_pct = round((att_t / tot_t) * 100) if tot_t > 0 else None
        practical_pct = round((att_p / tot_p) * 100) if tot_p > 0 else None

        grand_total += total
        grand_attended += attended

        status = "safe"
        if pct < 50:
            status = "critical"
        elif pct < 75:
            status = "at_risk"

        subject_wise.append({
            "subject": d["subject"],
            "code": d["code"],
            "faculty": d["faculty"],
            "total_lectures": total,
            "total_theory": tot_t,
            "total_practical": tot_p,
            "attended": attended,
            "theory_attendance": theory_pct,
            "practical_attendance": practical_pct,
            "attendance_pct": pct,
            "status": status,
            # Lectures needed to reach 75%: ceil((0.75*total - attended) / 0.25)
            "lectures_needed": max(0, -(-((75 * total // 100) + 1 - attended) // 1)) if pct < 75 else 0
        })

    overall_pct = round((grand_attended / grand_total) * 100) if grand_total > 0 else 0
    is_defaulter = overall_pct < 75
    defaulter_status = "Critical" if overall_pct < 50 else ("At Risk" if is_defaulter else None)

    # Recent 10 lectures for this class (for timetable/recent view)
    recent_lectures_result = await db.execute(
        select(LectureAttendance, Class.name, Subject.name, User.first_name, User.last_name)
        .join(Class, LectureAttendance.class_id == Class.id)
        .join(Subject, LectureAttendance.subject_id == Subject.id)
        .join(User, LectureAttendance.faculty_id == User.id)
        .where(Class.name == division)
        .order_by(LectureAttendance.lecture_date.desc(), LectureAttendance.created_at.desc())
    )
    recent_all = recent_lectures_result.all()
    recent_lectures = []
    for lec, c_name, s_name, f_first, f_last in recent_all[:20]:
        absentees = [str(r).strip() for r in (lec.absentee_roll_numbers or [])]
        raw_st = lec.session_type or "Theory"
        if raw_st in ("Lecture", "lecture"): raw_st = "Theory"
        elif raw_st in ("Lab", "lab"): raw_st = "Practical"
        recent_lectures.append({
            "date": lec.lecture_date.strftime("%b %d, %Y"),
            "subject": s_name,
            "session_type": raw_st,
            "time_slot": lec.time_slot,
            "topic": lec.topic_covered,
            "faculty": f"{f_first} {f_last}",
            "present": roll not in absentees,
            "total": lec.total_students_enrolled,
        })

    return StandardResponse(
        success=True,
        data={
            "roll_number": roll,
            "division": division,
            "overall_attendance": overall_pct,
            "total_theory": sum(d["total_theory"] for d in subject_map.values()),
            "total_practical": sum(d["total_practical"] for d in subject_map.values()),
            "attended_theory": sum(d["total_theory"] - d["absent_theory"] for d in subject_map.values()),
            "attended_practical": sum(d["total_practical"] - d["absent_practical"] for d in subject_map.values()),
            "subject_wise": subject_wise,
            "recent_lectures": recent_lectures,
            "is_defaulter": is_defaulter,
            "defaulter_status": defaulter_status,
        },
        error=None
    )

allow_hod = RoleChecker([RoleEnum.HOD])


@router.post("/generate", response_model=StandardResponse)
def generate_defaulter_list(
    division: str,
    month: str,
    current_user: User = Depends(allow_hod),
    db: Session = Depends(get_db)
):
    # Here we would normally calculate the attendance percentage for the given month and division
    # For now, let's just find all students in that division and arbitrarily pick some for the simulation.
    
    students = db.query(StudentProfile).filter(StudentProfile.division == division).all()
    
    # Simulate calculating defaulters (e.g., first 2 students)
    defaulter_ids = [str(s.user_id) for s in students[:2]] if students else []
    
    new_defaulter_list = DefaulterList(
        generated_by=current_user.id,
        division=division,
        month=month,
        student_ids=defaulter_ids,
        broadcast_status="PENDING"
    )
    db.add(new_defaulter_list)
    db.commit()
    db.refresh(new_defaulter_list)
    
    return StandardResponse(
        success=True,
        data=DefaulterListResponse.model_validate(new_defaulter_list),
        error=None
    )

@router.post("/broadcast/{list_id}", response_model=StandardResponse)
def broadcast_defaulter_list(
    list_id: str,
    current_user: User = Depends(allow_hod),
    db: Session = Depends(get_db)
):
    defaulter_list = db.query(DefaulterList).filter(DefaulterList.id == list_id).first()
    if not defaulter_list:
         return StandardResponse(
            success=False,
            data=None,
            error="Defaulter list not found"
        )
        
    defaulter_list.broadcast_status = "SENT"
    db.commit()
    db.refresh(defaulter_list)
    
    return StandardResponse(
        success=True,
        data=DefaulterListResponse.model_validate(defaulter_list),
        error=None
    )

@router.get("/excel/master")
async def download_master_excel(class_name: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(allow_faculty_hod)):
    # Fetch all lectures for this class
    lectures_query = await db.execute(
        select(LectureAttendance, Class.name, Subject.name)
        .join(Class, LectureAttendance.class_id == Class.id)
        .join(Subject, LectureAttendance.subject_id == Subject.id)
        .where(Class.name == class_name)
        .order_by(Class.name, Subject.name, LectureAttendance.lecture_date)
    )
    lectures = lectures_query.all()

    class_data = {}
    for lecture, c_name, subject_name in lectures:
        key = f"{c_name} - {subject_name}"
        if key not in class_data:
            class_data[key] = {
                "total_theory": 0,
                "total_practical": 0,
                "absentees": {},
                "class_name": c_name,
                "subject_name": subject_name
            }
            
        session_type = lecture.session_type or "Theory"
        if session_type == "Lecture": session_type = "Theory"
            
        if session_type == "Theory":
            class_data[key]["total_theory"] += 1
        else:
            class_data[key]["total_practical"] += 1

        absentees = lecture.absentee_roll_numbers or []
        for roll in absentees:
            roll = str(roll).strip()
            if roll:
                if roll not in class_data[key]["absentees"]:
                    class_data[key]["absentees"][roll] = {"Theory": 0, "Practical": 0}
                class_data[key]["absentees"][roll][session_type] += 1

    students_res = await db.execute(
        select(StudentProfile, User)
        .join(User, StudentProfile.user_id == User.id)
        .where(StudentProfile.division == class_name)
    )
    students = students_res.all()
    students_list = [
        {"roll_number": sp.roll_number, "name": f"{u.first_name} {u.last_name}"}
        for sp, u in students
    ]
    try:
        excel_bytes = excel_sync_agent.generate_master_sheet(class_name, students_list, class_data)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=Master_Attendance_{class_name}.xlsx"}
        )
    except Exception as e:
        import traceback
        with open("error.log", "a") as f:
            f.write(f"Master Excel Generate Error:\\n{traceback.format_exc()}\\n")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/excel/subject")
async def download_subject_excel(class_name: str, subject_name: str, faculty_name: str, session_type: str, db: AsyncSession = Depends(get_db)):
    # Fetch all historical lectures for this specific grouping
    all_res = await db.execute(
        select(LectureAttendance, Class.name, Subject.name, User.first_name, User.last_name)
        .join(Class, LectureAttendance.class_id == Class.id)
        .join(Subject, LectureAttendance.subject_id == Subject.id)
        .join(User, LectureAttendance.faculty_id == User.id)
        .where(
            Class.name == class_name,
            Subject.name == subject_name,
        )
        .order_by(LectureAttendance.lecture_date)
    )
    all_lectures = all_res.all()
    
    # Filter by exact faculty and session type
    filtered_lectures = []
    total_students_enrolled = 0
    for lec, c_name, s_name, f_first, f_last in all_lectures:
        raw_st = lec.session_type or "Theory"
        if raw_st in ("Lecture", "lecture"): raw_st = "Theory"
        elif raw_st in ("Lab", "lab"): raw_st = "Practical"
        
        f_name = f"{f_first} {f_last}"
        if f_name == faculty_name and raw_st == session_type:
            filtered_lectures.append({
                "lecture_date": lec.lecture_date,
                "time_slot": lec.time_slot,
                "absentee_roll_numbers": lec.absentee_roll_numbers or []
            })
            if lec.total_students_enrolled > total_students_enrolled:
                total_students_enrolled = lec.total_students_enrolled
                
    if not filtered_lectures:
        raise HTTPException(status_code=404, detail="No attendance records found for this subject.")
        
    # Fetch all students indexed by division for name lookup
    all_students_res = await db.execute(
        select(StudentProfile, User).join(User, StudentProfile.user_id == User.id)
    )
    name_lookup = {
        str(sp.roll_number): f"{u.first_name} {u.last_name}"
        for sp, u in all_students_res.all()
    }
    
    try:
        excel_bytes = excel_sync_agent.generate_subject_sheet(
            all_lectures_data=filtered_lectures,
            name_lookup=name_lookup,
            faculty_name=faculty_name,
            class_name=class_name,
            subject_name=subject_name,
            session_type=session_type,
            total_students=total_students_enrolled
        )
        filename = f"{subject_name}_{faculty_name}_{session_type}.xlsx".replace(" ", "_")
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        import traceback
        with open("error.log", "a") as f:
            f.write(f"Subject Excel Generate Error:\\n{traceback.format_exc()}\\n")
        raise HTTPException(status_code=500, detail=str(e))

