"""Add trigram index for job descriptions."""

from typing import Sequence, Union

from alembic import op

revision: str = "be9f733045e8"
down_revision: Union[str, Sequence[str], None] = "5875eaba982a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX ix_jobs_description_trgm "
        "ON jobs USING gin (description gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_jobs_description_trgm")
