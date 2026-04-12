"""Migrate username

Revision ID: 860c93909ea8
Revises: f681f29dc8fe
Create Date: 2026-04-12 21:19:31.735533

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "860c93909ea8"
down_revision: Union[str, Sequence[str], None] = "f681f29dc8fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "user",
        "username",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
    )
    op.create_unique_constraint("unique_username", "user", ["username"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_username", "user", type_="unique")
    op.alter_column(
        "user",
        "username",
        existing_type=sa.VARCHAR(length=255),
        nullable=True,
    )
