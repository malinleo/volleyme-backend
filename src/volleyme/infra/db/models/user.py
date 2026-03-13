from __future__ import annotations

import typing

import sqlalchemy
import sqlalchemy.orm

from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .event import Event, EventHostRel, EventParticipantRel
    from .event_invitation import EventInvitation
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
        lazy="raise",
    )
    participated_events: sqlalchemy.orm.Mapped[list[Event]] = (
        sqlalchemy.orm.relationship(
            "Event",
            secondary="event_participant_rel",
            back_populates="participants",
            lazy="raise",
        )
    )
    participated_events_rel: sqlalchemy.orm.Mapped[list[EventParticipantRel]] = (
        sqlalchemy.orm.relationship(
            "EventParticipantRel",
            back_populates="user",
            cascade="all, delete-orphan",
            lazy="raise",
        )
    )
    hosted_events: sqlalchemy.orm.Mapped[list[Event]] = sqlalchemy.orm.relationship(
        "Event",
        secondary="event_host_rel",
        back_populates="hosts",
        lazy="raise",
    )
    hosted_events_rel: sqlalchemy.orm.Mapped[list[EventHostRel]] = (
        sqlalchemy.orm.relationship(
            "EventHostRel",
            back_populates="user",
            cascade="all, delete-orphan",
            lazy="raise",
        )
    )
    created_events: sqlalchemy.orm.Mapped[list[Event]] = sqlalchemy.orm.relationship(
        "Event",
        back_populates="created_by",
        foreign_keys="Event.created_by_id",
        lazy="raise",
    )
    updated_events: sqlalchemy.orm.Mapped[list[Event]] = sqlalchemy.orm.relationship(
        "Event",
        back_populates="updated_by",
        foreign_keys="Event.updated_by_id",
        lazy="raise",
    )
    invitations: sqlalchemy.orm.Mapped[list[EventInvitation]] = (
        sqlalchemy.orm.relationship(
            "EventInvitation",
            back_populates="user",
            foreign_keys="EventInvitation.user_id",
            lazy="raise",
        )
    )
