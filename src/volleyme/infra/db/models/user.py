from __future__ import annotations

import typing

import sqlalchemy
import sqlalchemy.orm

from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .event import Event, EventHostRel
    from .profile import Profile


class User(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "user"

    email: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(254),
        unique=True,
    )
    password: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
    )
    profile: sqlalchemy.orm.Mapped[Profile | None] = sqlalchemy.orm.relationship(
        "Profile",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    hosted_events: sqlalchemy.orm.Mapped[list[Event]] = sqlalchemy.orm.relationship(
        "Event",
        secondary="event_host_rel",
        back_populates="hosts",
    )
    hosted_events_rel: sqlalchemy.orm.Mapped[list[EventHostRel]] = (
        sqlalchemy.orm.relationship(
            "EventHostRel",
            back_populates="user",
        )
    )
