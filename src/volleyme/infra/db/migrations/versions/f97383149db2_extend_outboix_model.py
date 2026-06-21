"""Extend outboix model

Revision ID: f97383149db2
Revises: dc215fa30d6d
Create Date: 2026-06-21 12:35:20.419911

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f97383149db2"
down_revision: Union[str, Sequence[str], None] = "dc215fa30d6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "outbox",
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("outbox", sa.Column("last_error", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("outbox", "last_error")
    op.drop_column("outbox", "processing_started_at")
