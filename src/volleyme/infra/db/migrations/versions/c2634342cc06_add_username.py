"""Add username

Revision ID: c2634342cc06
Revises: 131477948ade
Create Date: 2026-04-12 21:12:35.927318

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2634342cc06"
down_revision: Union[str, Sequence[str], None] = "131477948ade"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user", sa.Column("username", sa.String(length=255), nullable=True))
    op.alter_column(
        "user",
        "email",
        existing_type=sa.VARCHAR(length=254),
        nullable=True,
    )
    op.drop_constraint(op.f("user_email_key"), "user", type_="unique")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(
        op.f("user_email_key"),
        "user",
        ["email"],
        postgresql_nulls_not_distinct=False,
    )
    op.alter_column(
        "user",
        "email",
        existing_type=sa.VARCHAR(length=254),
        nullable=False,
    )
    op.drop_column("user", "username")
