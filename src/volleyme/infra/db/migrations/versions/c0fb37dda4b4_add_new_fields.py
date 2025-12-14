"""add new fields

Revision ID: c0fb37dda4b4
Revises: 0b5946bbe66c
Create Date: 2025-12-13 20:22:09.415159

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c0fb37dda4b4"
down_revision: Union[str, Sequence[str], None] = "0b5946bbe66c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "event", sa.Column("end_dt", sa.DateTime(timezone=True), nullable=False)
    )
    op.add_column("event", sa.Column("format_type", sa.SmallInteger(), nullable=False))
    op.add_column("event", sa.Column("country", sa.String(length=2), nullable=False))
    op.add_column("event", sa.Column("city", sa.String(length=255), nullable=False))
    op.add_column("event", sa.Column("address", sa.String(length=1024), nullable=False))
    op.add_column(
        "event", sa.Column("max_participants_count", sa.Integer(), nullable=False)
    )
    op.add_column("event", sa.Column("currency", sa.String(length=3), nullable=False))
    op.alter_column(
        "event",
        "price",
        existing_type=sa.INTEGER(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=False,
    )
    op.alter_column("event", "type", new_column_name="game_type")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("event", "game_type", new_column_name="type")
    op.alter_column(
        "event",
        "price",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.drop_column("event", "currency")
    op.drop_column("event", "max_participants_count")
    op.drop_column("event", "address")
    op.drop_column("event", "city")
    op.drop_column("event", "country")
    op.drop_column("event", "format_type")
    op.drop_column("event", "end_dt")
