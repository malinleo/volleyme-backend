"""Add unique constraints to m2m tables

Revision ID: ea0ddc49b3b4
Revises: 38880e436700
Create Date: 2025-12-16 21:15:33.311825

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea0ddc49b3b4"
down_revision: Union[str, Sequence[str], None] = "38880e436700"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "unique_event_host_pair",
        "event_host_rel",
        ["event_id", "user_id"],
    )
    op.create_unique_constraint(
        "unique_event_participant_pair",
        "event_participant_rel",
        ["event_id", "user_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "unique_event_participant_pair",
        "event_participant_rel",
        type_="unique",
    )
    op.drop_constraint("unique_event_host_pair", "event_host_rel", type_="unique")
