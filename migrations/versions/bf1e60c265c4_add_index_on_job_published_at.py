"""Add index on job published_at."""

from collections.abc import Sequence

from alembic import op

revision: str = "bf1e60c265c4"
down_revision: str | Sequence[str] | None = "be9f733045e8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_jobs_published_at",
        "jobs",
        ["published_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_published_at", table_name="jobs")
