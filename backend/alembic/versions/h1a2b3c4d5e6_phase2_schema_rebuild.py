"""Phase 2 schema rebuild: new modular tables

Revision ID: h1a2b3c4d5e6
Revises: g9f7h2k3j4l5
Create Date: 2026-07-17 18:00:00.000000

This migration adds the 8 new tables from the modular redesign:
- departments
- academic_years
- enrollments
- class_subjects
- attendance_sessions
- attendance_records
- grades
- kt_records
- certificates

And modifies:
- classes: adds academic_year_id FK, year_level, division, semester; drops name/department_id(str)/total_students
- subjects: adds credits, is_active, updated_at; drops old fields
- student_profiles: maps department_id FK to new departments table
- faculty_profiles: maps department_id FK to new departments table
- users: adds is_active column; updates RoleEnum values to lowercase
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'h1a2b3c4d5e6'
down_revision: Union[str, None] = 'g9f7h2k3j4l5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create departments table
    op.create_table('departments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=True)

    # 2. Create academic_years table
    op.create_table('academic_years',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_academic_years_name'), 'academic_years', ['name'], unique=True)

    # 3. Add is_active to users and update role enum
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    # Note: RoleEnum values are now lowercase (student/faculty/hod/admin).
    # Existing data migration is handled by seed script re-seeding from scratch.
    
    # 4. Add department_id FK to faculty_profiles and student_profiles
    # First insert a placeholder "General" department
    op.execute(
        "INSERT INTO departments (id, code, name) VALUES (gen_random_uuid(), 'GENERAL', 'General') ON CONFLICT (code) DO NOTHING"
    )
    op.execute(
        "INSERT INTO departments (id, code, name) VALUES (gen_random_uuid(), 'AIDS', 'Artificial Intelligence and Data Science') ON CONFLICT (code) DO NOTHING"
    )
    
    # Add department_id to faculty_profiles (using "GENERAL" as fallback)
    op.add_column('faculty_profiles',
        sa.Column('department_id', sa.Uuid(), nullable=True)
    )
    op.add_column('faculty_profiles',
        sa.Column('employee_code', sa.String(length=50), nullable=True)
    )
    op.add_column('faculty_profiles',
        sa.Column('full_name', sa.String(length=255), nullable=True)
    )
    op.add_column('faculty_profiles',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, server_onupdate=sa.text('now()'))
    )
    # Backfill department_id for existing faculty
    op.execute(
        "UPDATE faculty_profiles fp SET department_id = (SELECT id FROM departments WHERE code = 'AIDS' LIMIT 1) "
        "WHERE fp.department_id IS NULL"
    )
    # Create FK
    op.create_foreign_key('fk_faculty_profiles_department_id', 'faculty_profiles', 'departments', ['department_id'], ['id'])

    # Add department_id to student_profiles
    op.add_column('student_profiles',
        sa.Column('department_id', sa.Uuid(), nullable=True)
    )
    op.add_column('student_profiles',
        sa.Column('full_name', sa.String(length=255), nullable=True)
    )
    op.add_column('student_profiles',
        sa.Column('admission_year', sa.Integer(), nullable=True)
    )
    op.add_column('student_profiles',
        sa.Column('graduation_year', sa.Integer(), nullable=True)
    )
    op.add_column('student_profiles',
        sa.Column('status', sa.String(length=20), nullable=False, server_default='enrolled')
    )
    op.add_column('student_profiles',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    # Backfill department_id
    op.execute(
        "UPDATE student_profiles sp SET department_id = (SELECT id FROM departments WHERE code = 'AIDS' LIMIT 1) "
        "WHERE sp.department_id IS NULL"
    )
    op.create_foreign_key('fk_student_profiles_department_id', 'student_profiles', 'departments', ['department_id'], ['id'])

    # 5. Modify classes table - add new relational columns and convert department_id to UUID
    op.drop_column('classes', 'department_id')
    op.add_column('classes', sa.Column('department_id', sa.Uuid(), nullable=False))
    op.create_foreign_key('fk_classes_department_id', 'classes', 'departments', ['department_id'], ['id'], ondelete='CASCADE')
    op.add_column('classes', sa.Column('academic_year_id', sa.Uuid(), nullable=True))
    op.add_column('classes', sa.Column('year_level', sa.Integer(), nullable=True))
    op.add_column('classes', sa.Column('division', sa.String(length=10), nullable=True))
    op.add_column('classes', sa.Column('semester', sa.Integer(), nullable=True))
    op.add_column('classes', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    # 6. Modify subjects table - add credits, is_active, updated_at, and convert department_id to UUID
    op.drop_column('subjects', 'department_id')
    op.add_column('subjects', sa.Column('department_id', sa.Uuid(), nullable=False))
    op.create_foreign_key('fk_subjects_department_id', 'subjects', 'departments', ['department_id'], ['id'], ondelete='CASCADE')
    op.add_column('subjects', sa.Column('credits', sa.Integer(), nullable=False, server_default='3'))
    conn = op.get_bind()
inspector = sa.inspect(conn)
subject_cols = [c["name"] for c in inspector.get_columns("subjects")]
if "semester" not in subject_cols:
    op.add_column('subjects', sa.Column('semester', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('subjects', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('subjects', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('subjects', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))


    # 7. Create class_subjects junction table
    op.create_table('class_subjects',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('class_id', sa.Uuid(), nullable=False),
        sa.Column('subject_id', sa.Uuid(), nullable=False),
        sa.Column('faculty_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['faculty_id'], ['faculty_profiles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('class_id', 'subject_id', name='uq_class_subject')
    )

    # 8. Create attendance_sessions (replaces lecture_attendances for new records)
    op.create_table('attendance_sessions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('class_subject_id', sa.Uuid(), nullable=True),  # Nullable for backward compat
        sa.Column('faculty_id', sa.Uuid(), nullable=False),
        sa.Column('class_id', sa.Uuid(), nullable=False),
        sa.Column('subject_id', sa.Uuid(), nullable=False),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('time_slot', sa.String(length=50), nullable=True),
        sa.Column('topic_covered', sa.String(length=200), nullable=True),
        sa.Column('total_students_enrolled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('students_present_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('absentee_roll_numbers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('session_type', sa.String(length=20), nullable=False, server_default='Theory'),
        sa.Column('academic_year', sa.String(length=20), nullable=False, server_default='2026-2027'),
        sa.Column('semester', sa.String(length=10), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['faculty_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Create attendance_records
    op.create_table('attendance_records',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('attendance_session_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('marked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['attendance_session_id'], ['attendance_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('attendance_session_id', 'student_id', name='uq_attendance_session_student')
    )

    # 10. Create enrollments
    op.create_table('enrollments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('class_id', sa.Uuid(), nullable=False),
        sa.Column('academic_year_id', sa.Uuid(), nullable=False),
        sa.Column('semester', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['class_id'], ['classes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'academic_year_id', 'semester', name='uq_student_academic_period_enrollment')
    )

    # 11. Create grades
    op.create_table('grades',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('subject_id', sa.Uuid(), nullable=False),
        sa.Column('academic_year_id', sa.Uuid(), nullable=False),
        sa.Column('semester', sa.Integer(), nullable=False),
        sa.Column('internal_marks', sa.Numeric(), nullable=False, server_default='0'),
        sa.Column('external_marks', sa.Numeric(), nullable=False, server_default='0'),
        sa.Column('total_marks', sa.Numeric(), nullable=False, server_default='0'),
        sa.Column('grade_letter', sa.String(length=5), nullable=False),
        sa.Column('grade_point', sa.Numeric(), nullable=False, server_default='0'),
        sa.Column('result_status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'subject_id', 'academic_year_id', 'semester', name='uq_student_subject_attempt')
    )

    # 12. Create kt_records
    op.create_table('kt_records',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('subject_id', sa.Uuid(), nullable=False),
        sa.Column('academic_year_id', sa.Uuid(), nullable=False),
        sa.Column('semester', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('cleared_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['academic_year_id'], ['academic_years.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'subject_id', 'academic_year_id', 'semester', name='uq_student_kt_occurrence')
    )

    # 13. Create certificates
    op.create_table('certificates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('event_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('issuing_body', sa.String(length=255), nullable=False),
        sa.Column('date_achieved', sa.Date(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size_kb', sa.Integer(), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('verified_by', sa.Uuid(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('certificates')
    op.drop_table('kt_records')
    op.drop_table('grades')
    op.drop_table('enrollments')
    op.drop_table('attendance_records')
    op.drop_table('attendance_sessions')
    op.drop_table('class_subjects')
    
    # Remove added columns from subjects and restore department_id string
    op.drop_constraint('fk_subjects_department_id', 'subjects', type_='foreignkey')
    op.drop_column('subjects', 'department_id')
    op.add_column('subjects', sa.Column('department_id', sa.String(length=100), nullable=True))
    op.drop_column('subjects', 'updated_at')
    op.drop_column('subjects', 'created_at')
    op.drop_column('subjects', 'is_active')
    op.drop_column('subjects', 'semester')
    op.drop_column('subjects', 'credits')
    
    # Remove added columns from classes and restore department_id string
    op.drop_constraint('fk_classes_department_id', 'classes', type_='foreignkey')
    op.drop_column('classes', 'department_id')
    op.add_column('classes', sa.Column('department_id', sa.String(length=100), nullable=True))
    op.drop_column('classes', 'created_at')
    op.drop_column('classes', 'semester')
    op.drop_column('classes', 'division')
    op.drop_column('classes', 'year_level')
    op.drop_column('classes', 'academic_year_id')

    # Remove FKs and columns from student/faculty profiles
    op.drop_constraint('fk_student_profiles_department_id', 'student_profiles', type_='foreignkey')
    op.drop_column('student_profiles', 'updated_at')
    op.drop_column('student_profiles', 'status')
    op.drop_column('student_profiles', 'graduation_year')
    op.drop_column('student_profiles', 'admission_year')
    op.drop_column('student_profiles', 'full_name')
    op.drop_column('student_profiles', 'department_id')
    
    op.drop_constraint('fk_faculty_profiles_department_id', 'faculty_profiles', type_='foreignkey')
    op.drop_column('faculty_profiles', 'updated_at')
    op.drop_column('faculty_profiles', 'full_name')
    op.drop_column('faculty_profiles', 'employee_code')
    op.drop_column('faculty_profiles', 'department_id')
    
    # Remove from users
    op.drop_column('users', 'is_active')

    op.drop_index(op.f('ix_academic_years_name'), table_name='academic_years')
    op.drop_table('academic_years')
    op.drop_index(op.f('ix_departments_code'), table_name='departments')
    op.drop_table('departments')
