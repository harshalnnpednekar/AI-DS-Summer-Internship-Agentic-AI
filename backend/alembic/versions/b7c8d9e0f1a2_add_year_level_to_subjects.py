"""add year level to subjects

Revision ID: b7c8d9e0f1a2
Revises: h1a2b3c4d5e6
Create Date: 2026-07-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "h1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subjects", sa.Column("year_level", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE subjects "
        "SET year_level = ((semester + 1) / 2) "
        "WHERE year_level IS NULL"
    )
    op.alter_column("subjects", "year_level", nullable=False)
    op.create_check_constraint(
        "ck_subjects_year_level_range",
        "subjects",
        "year_level BETWEEN 1 AND 4",
    )


def downgrade() -> None:
    op.drop_constraint("ck_subjects_year_level_range", "subjects", type_="check")
    op.drop_column("subjects", "year_level")
