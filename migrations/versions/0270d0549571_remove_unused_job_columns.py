"""Remove unused job columns.

Revision ID: 0270d0549571
Revises: 49e27308a1ab
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0270d0549571"
down_revision: str | None = "49e27308a1ab"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_column("jobs", "employment_type")
    op.drop_column("jobs", "contract_type")
    op.drop_column("jobs", "work_mode")


def downgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("work_mode", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("contract_type", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("employment_type", sa.String(length=255), nullable=True),
    )
