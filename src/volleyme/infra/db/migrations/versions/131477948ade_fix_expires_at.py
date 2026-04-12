"""Fix expires_at

Revision ID: 131477948ade
Revises: 1b2ae830ce95
Create Date: 2026-03-14 00:39:22.800929

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "131477948ade"
down_revision: Union[str, Sequence[str], None] = "1b2ae830ce95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "event_invitation",
        "expires_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "event_invitation",
        "expires_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
