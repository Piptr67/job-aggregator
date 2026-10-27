"""add email verification fields

Revision ID: a1d1033a8540
Revises: ed7852b95657
Create Date: 2026-10-20 16:37:53.423455

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1d1033a8540"
down_revision: str | Sequence[str] | None = "ed7852b95657"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "is_verified", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.alter_column("users", "is_verified", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_verified")
