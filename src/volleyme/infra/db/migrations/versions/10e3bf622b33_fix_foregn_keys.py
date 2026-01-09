"""fix foregn keys

Revision ID: 10e3bf622b33
Revises: ea0ddc49b3b4
Create Date: 2026-01-09 23:38:25.310827

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "10e3bf622b33"
down_revision: Union[str, Sequence[str], None] = "ea0ddc49b3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("event_host_rel_user_id_fkey"), "event_host_rel", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("event_host_rel_event_id_fkey"), "event_host_rel", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_event_host_rel_event_id",
        "event_host_rel",
        "event",
        ["event_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_event_host_rel_user_id",
        "event_host_rel",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        op.f("fk_event_participant_rel_user_id"),
        "event_participant_rel",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("event_participant_rel_event_id_fkey"),
        "event_participant_rel",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_event_participant_rel_user_id",
        "event_participant_rel",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_event_participant_rel_event_id",
        "event_participant_rel",
        "event",
        ["event_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_event_participant_rel_event_id", "event_participant_rel", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_event_participant_rel_user_id", "event_participant_rel", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("event_participant_rel_event_id_fkey"),
        "event_participant_rel",
        "event",
        ["event_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_event_participant_rel_user_id"),
        "event_participant_rel",
        "user",
        ["user_id"],
        ["id"],
    )
    op.drop_constraint(
        "fk_event_host_rel_user_id", "event_host_rel", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_event_host_rel_event_id", "event_host_rel", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("event_host_rel_event_id_fkey"),
        "event_host_rel",
        "event",
        ["event_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("event_host_rel_user_id_fkey"),
        "event_host_rel",
        "user",
        ["user_id"],
        ["id"],
    )
