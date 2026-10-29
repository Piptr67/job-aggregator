"""Add index on job published_at."""

from typing import Sequence, Union

from alembic import op

revision: str = "bf1e60c265c4"
down_revision: Union[str, Sequence[str], None] = "be9f733045e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_jobs_published_at",
        "jobs",
        ["published_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_published_at", table_name="jobs")
