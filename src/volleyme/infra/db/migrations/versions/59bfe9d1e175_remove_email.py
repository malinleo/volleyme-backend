"""Remove email

Revision ID: 59bfe9d1e175
Revises: 860c93909ea8
Create Date: 2026-04-12 22:33:03.877467

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59bfe9d1e175"
down_revision: Union[str, Sequence[str], None] = "860c93909ea8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("user", "email")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "user",
        sa.Column("email", sa.VARCHAR(length=254), autoincrement=False, nullable=True),
    )
