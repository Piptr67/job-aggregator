"""remove job description trigram index

Revision ID: 49e27308a1ab
Revises: bf1e60c265c4
Create Date: 2026-10-29 18:56:07.157107
"""

from collections.abc import Sequence

from alembic import op

revision: str = "49e27308a1ab"
down_revision: str | Sequence[str] | None = "bf1e60c265c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(
        op.f("ix_jobs_description_trgm"),
        table_name="jobs",
        postgresql_ops={"description": "gin_trgm_ops"},
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.create_index(
        op.f("ix_jobs_description_trgm"),
        "jobs",
        ["description"],
        unique=False,
        postgresql_ops={"description": "gin_trgm_ops"},
        postgresql_using="gin",
    )
