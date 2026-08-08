"""add_match_tracker_fields

Revision ID: e8a1c2b3d4f5
Revises: d1faf28e6a17
Create Date: 2026-08-08 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e8a1c2b3d4f5"
down_revision: Union[str, Sequence[str], None] = "d1faf28e6a17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "match_results",
        sa.Column("status", sa.String(length=32), server_default="matched", nullable=False),
    )
    op.add_column("match_results", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column(
        "match_results",
        sa.Column("status_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_match_results_status", "match_results", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_match_results_status", table_name="match_results")
    op.drop_column("match_results", "status_updated_at")
    op.drop_column("match_results", "notes")
    op.drop_column("match_results", "status")
