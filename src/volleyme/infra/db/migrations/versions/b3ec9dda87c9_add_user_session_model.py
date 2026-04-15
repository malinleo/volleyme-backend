"""Add user session model

Revision ID: b3ec9dda87c9
Revises: 5df5e5dddb73
Create Date: 2026-04-15 23:47:02.332772

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3ec9dda87c9"
down_revision: Union[str, Sequence[str], None] = "5df5e5dddb73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_session",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name="fk_user_session_user_id"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_user_session_user_id", "user_session", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_user_session_user_id", table_name="user_session")
    op.drop_table("user_session")
