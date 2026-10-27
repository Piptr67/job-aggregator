"""allow null password for Google users

Revision ID: 5875eaba982a
Revises: a1d1033a8540
Create Date: 2026-10-22 14:31:44.385451

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5875eaba982a"
down_revision: str | Sequence[str] | None = "a1d1033a8540"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users", "hashed_password", existing_type=sa.VARCHAR(length=255), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users", "hashed_password", existing_type=sa.VARCHAR(length=255), nullable=False
    )
