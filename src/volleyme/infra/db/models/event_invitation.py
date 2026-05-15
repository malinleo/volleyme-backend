from __future__ import annotations

import datetime
import typing
import uuid

import sqlalchemy.orm

from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .event import Event
    from .user import User


class EventInvitation(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "event_invitation"

    event_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("event.id", name="fk_event_invitation_event_id"),
    )
    event: sqlalchemy.orm.Mapped[Event] = sqlalchemy.orm.relationship(
        "Event",
        back_populates="invitations",
        lazy="raise",
    )
    user_id: sqlalchemy.orm.Mapped[uuid.UUID | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey(
            "user.id",
            name="fk_event_invitation_user_id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    user: sqlalchemy.orm.Mapped[User | None] = sqlalchemy.orm.relationship(
        "User",
        back_populates="invitations",
        foreign_keys=[user_id],
        lazy="raise",
    )
    token: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
        unique=True,
    )
    expires_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.DateTime(timezone=True),
            nullable=True,
        )
    )
    used_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.DateTime(timezone=True),
            nullable=True,
        )
    )
