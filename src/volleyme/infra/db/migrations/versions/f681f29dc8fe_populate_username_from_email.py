"""Migrate username

Revision ID: f681f29dc8fe
Revises: c2634342cc06
Create Date: 2026-04-12 21:15:00.466928

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f681f29dc8fe"
down_revision: Union[str, Sequence[str], None] = "c2634342cc06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "UPDATE \"user\" SET username = replace(split_part(email, '@', 1), '@', '_') WHERE username IS NULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
