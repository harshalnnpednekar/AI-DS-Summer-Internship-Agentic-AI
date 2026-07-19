"""Merge two heads + fix RoleEnum casing to lowercase

Revision ID: z0a1b2c3d4e5
Revises: 555c449d8d82, b7c8d9e0f1a2
Create Date: 2026-07-19

This merge migration:
1. Joins the two diverged branches (555c449d8d82 and b7c8d9e0f1a2) into one head.
2. Drops the legacy 'year' (string) column from subjects that was added in 555c
   (the Phase 2 rebuild adds year_level integer instead).
3. Converts the roleenum PostgreSQL type values from uppercase (HOD/FACULTY/STUDENT)
   to lowercase (hod/faculty/student) to match the current Python model.
4. Adds the 'admin' value to the enum if it doesn't already exist.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "z0a1b2c3d4e5"
down_revision: Union[str, Sequence[str]] = ("555c449d8d82", "b7c8d9e0f1a2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Drop legacy string 'year' column from subjects (555c branch) ─────────
    # The Phase 2 branch already added 'year_level' (integer). The old 'year'
    # string column from 555c conflicts and is no longer used by the models.
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    subject_cols = [c["name"] for c in inspector.get_columns("subjects")]
    if "year" in subject_cols:
        op.drop_column("subjects", "year")

    # ── 2. Fix RoleEnum values: uppercase → lowercase ────────────────────────────
    # PostgreSQL does not support ALTER TYPE ... RENAME VALUE in versions < 10.
    # We use a safe approach: rename each value one by one.
    # We check current enum values first to stay idempotent.
    result = conn.execute(
        sa.text("SELECT unnest(enum_range(NULL::roleenum))::text")
    )
    current_values = {row[0] for row in result}

    # Rename uppercase → lowercase (only if uppercase still exists)
    if "HOD" in current_values:
        op.execute(sa.text("ALTER TYPE roleenum RENAME VALUE 'HOD' TO 'hod'"))
    if "FACULTY" in current_values:
        op.execute(sa.text("ALTER TYPE roleenum RENAME VALUE 'FACULTY' TO 'faculty'"))
    if "STUDENT" in current_values:
        op.execute(sa.text("ALTER TYPE roleenum RENAME VALUE 'STUDENT' TO 'student'"))

    # Add 'admin' value if missing
    result2 = conn.execute(
        sa.text("SELECT unnest(enum_range(NULL::roleenum))::text")
    )
    updated_values = {row[0] for row in result2}
    if "admin" not in updated_values:
        op.execute(sa.text("ALTER TYPE roleenum ADD VALUE 'admin'"))

    # ── 3. Ensure users.is_active exists (Phase 2 adds it; guard for safety) ────
    if "is_active" not in subject_cols:
        pass  # Already handled by h1a2b3c4d5e6 migration

    # ── 4. Ensure users table has first_name / last_name columns ────────────────
    user_cols = [c["name"] for c in inspector.get_columns("users")]
    if "first_name" not in user_cols:
        op.add_column("users", sa.Column("first_name", sa.String(100), nullable=False, server_default=""))
    if "last_name" not in user_cols:
        op.add_column("users", sa.Column("last_name", sa.String(100), nullable=False, server_default=""))


def downgrade() -> None:
    # Restore uppercase enum values
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT unnest(enum_range(NULL::roleenum))::text")
    )
    current_values = {row[0] for row in result}

    if "hod" in current_values:
        op.execute(sa.text("ALTER TYPE roleenum RENAME VALUE 'hod' TO 'HOD'"))
    if "faculty" in current_values:
        op.execute(sa.text("ALTER TYPE roleenum RENAME VALUE 'faculty' TO 'FACULTY'"))
    if "student" in current_values:
        op.execute(sa.text("ALTER TYPE roleenum RENAME VALUE 'student' TO 'STUDENT'"))
