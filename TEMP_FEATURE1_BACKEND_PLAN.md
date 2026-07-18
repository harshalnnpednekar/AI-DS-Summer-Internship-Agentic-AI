# Temporary Feature 1 & Backend Normalization Plan

## Feature 1: Academic Year & Semester in Attendance

### Objective
Implement academic year and semester fields for attendance marking, fully connected between frontend and backend.

### Backend Changes
1. **Model updates**
   - Add `academic_year` (String, NOT NULL) to `LectureAttendance`
   - Add `semester` (String, NOT NULL) to `LectureAttendance`

2. **Database migration**
   - Create an Alembic migration that adds both columns to `lecture_attendances`
   - Use sensible defaults for existing records if needed

3. **Schema updates**
   - Add enum validations for academic year and semester in `backend/app/schemas.py`
   - Extend `LectureAttendanceSubmit` to include `academic_year` and `semester`

4. **API endpoint updates**
   - Use `/api/attendance/form-meta` to return valid academic years and semesters
   - Use `/api/attendance/submit` to accept and persist the new fields

5. **Frontend integration**
   - Add `academicYear` and `semester` state in `frontend/src/pages/MarkAttendance.jsx`
   - Fetch dropdown options from `/api/attendance/form-meta`
   - Include values in the submit payload
   - Validate the fields before submitting

### Validation & Security
- Ensure backend authorization is enforced via current user roles
- Ensure enum validation rejects invalid academic year or semester values
- Ensure attendance submit returns proper error messages when required fields are missing

## Proper Normalized Backend for Frontend

### Goals
- Provide clear REST endpoints for frontend usage
- Keep data normalized and avoid duplication
- Make relationships explicit with foreign keys
- Ensure the frontend can query only permitted data by role

### Suggested Normalized Schema

#### Users and Profiles
- `users`
  - `id`, `email`, `password_hash`, `first_name`, `last_name`, `role`, `created_at`, `updated_at`

- `faculty_profiles`
  - `id`, `user_id`, `department`, `designation`, `assigned_classes`, `phone`, `bio`, `joining_year`

- `student_profiles`
  - `id`, `user_id`, `roll_number`, `department`, `current_semester`, `division`, `phone`, `bio`, `joining_year`

#### Academic Entities
- `classes`
  - `id`, `name`, `department_id`, `total_students`

- `subjects`
  - `id`, `code`, `name`, `department_id`

- `faculty_subject_mappings`
  - `id`, `faculty_id`, `class_id`, `subject_id`

#### Attendance
- `lecture_attendances`
  - `id`, `faculty_id`, `class_id`, `subject_id`, `lecture_date`, `time_slot`, `topic_covered`, `total_students_enrolled`, `students_present_count`, `absentee_roll_numbers`, `session_type`, `academic_year`, `semester`, `created_at`

- `defaulter_lists`
  - `id`, `generated_by`, `division`, `month`, `generated_at`, `student_ids`, `broadcast_status`

### Recommended Backend Patterns

1. **Service layer**
   - Use a dedicated `services/attendance.py` for business logic
   - Keep route handlers lightweight

2. **Normalized queries**
   - Use joins to fetch related data for forms and dashboards
   - Avoid storing redundant class or subject names in the attendance table

3. **Role-aware access**
   - Faculty: only allowed to submit for subjects mapped to them
   - HOD: able to view department-level dashboards and attendance stats
   - Student: able to view only their own attendance and defaulter status

4. **API contract for frontend**
   - `/api/auth/login`
   - `/api/auth/signup`
   - `/api/attendance/form-meta`
   - `/api/attendance/submit`
   - `/api/attendance/stats`
   - `/api/users/me`

### Frontend Backend Contract

The frontend should rely on a stable, normalized API:
- Fetch classes and subjects via `form-meta`
- Submit attendance with normalized IDs
- Receive backend validation errors in a consistent response format
- Use JWT token auth and proxy `/api` to backend via Vite

## Notes
- This file is temporary and should be used as a plan for implementing Feature 1 and normalizing backend design.
- The actual implementation should follow the existing FastAPI and React structure in the project.
