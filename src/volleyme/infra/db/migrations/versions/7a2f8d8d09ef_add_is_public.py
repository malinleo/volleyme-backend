"""add is_public

Revision ID: 7a2f8d8d09ef
Revises: 10e3bf622b33
Create Date: 2026-03-05 01:37:00.747406

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a2f8d8d09ef"
down_revision: Union[str, Sequence[str], None] = "10e3bf622b33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "event",
        sa.Column(
            "is_public", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("event", "is_public")
