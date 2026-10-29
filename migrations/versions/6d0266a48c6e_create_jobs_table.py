"""create jobs table

Revision ID: 6d0266a48c6e
Revises:
Create Date: 2026-09-24 17:40:33.362504

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6d0266a48c6e"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=255), nullable=True),
        sa.Column("contract_type", sa.String(length=255), nullable=True),
        sa.Column("work_mode", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("jobs")
