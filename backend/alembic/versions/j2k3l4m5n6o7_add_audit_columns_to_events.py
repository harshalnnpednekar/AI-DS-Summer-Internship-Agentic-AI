"""add missing audit columns to events table

Revision ID: j2k3l4m5n6o7
Revises: z0a1b2c3d4e5
Create Date: 2026-07-19 22:30:00.000000

The original events table (from the initial migration) never included
created_by, created_at, or updated_at columns, even though the Event
model has always expected them. This adds the missing columns.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j2k3l4m5n6o7'
down_revision: Union[str, None] = 'z0a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    event_cols = [c["name"] for c in inspector.get_columns("events")]

    if "created_by" not in event_cols:
        op.add_column('events', sa.Column('created_by', sa.Uuid(), nullable=True))
        op.create_foreign_key(
            'fk_events_created_by', 'events', 'users', ['created_by'], ['id'], ondelete='SET NULL'
        )
    if "created_at" not in event_cols:
        op.add_column(
            'events',
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
        )
    if "updated_at" not in event_cols:
        op.add_column(
            'events',
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
        )


def downgrade() -> None:
    op.drop_constraint('fk_events_created_by', 'events', type_='foreignkey')
    op.drop_column('events', 'created_by')
    op.drop_column('events', 'created_at')
    op.drop_column('events', 'updated_at')