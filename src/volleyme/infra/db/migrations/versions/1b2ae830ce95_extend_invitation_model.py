"""Extend invitation model

Revision ID: 1b2ae830ce95
Revises: 9990f24667ea
Create Date: 2026-03-06 01:41:04.978067

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1b2ae830ce95"
down_revision: Union[str, Sequence[str], None] = "9990f24667ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "event_invitation",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column(
        "event_invitation",
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("event_invitation", "used_at")
    op.drop_column("event_invitation", "expires_at")
