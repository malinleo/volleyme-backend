from __future__ import annotations

import datetime
import decimal
import typing
import uuid

import sqlalchemy.orm

from src.common.models import base as base_models
from src.volleyme.domain import enums

if typing.TYPE_CHECKING:
    from .game import Game
    from .player import Player
    from .user import User


class Event(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "event"

    start_dt: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
    )
    end_dt: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
    )
    title: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(255),
    )
    game_type: sqlalchemy.orm.Mapped[enums.GameType] = sqlalchemy.orm.mapped_column(
        sqlalchemy.SmallInteger,
    )
    format_type: sqlalchemy.orm.Mapped[enums.EventFormatType] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.SmallInteger,
        )
    )
    country: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(2),
    )
    city: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(255),
    )
    address: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(1024),
    )
    max_participants_count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Integer,
        default=0,
    )
    participants: sqlalchemy.orm.Mapped[list[Player]] = sqlalchemy.orm.relationship(
        "Player",
        secondary="event_participant_rel",
        back_populates="events",
    )
    participants_rel: sqlalchemy.orm.Mapped[list[EventParticipantRel]] = (
        sqlalchemy.orm.relationship(
            "EventParticipantRel",
            back_populates="event",
        )
    )
    hosts: sqlalchemy.orm.Mapped[list[User]] = sqlalchemy.orm.relationship(
        "User",
        secondary="event_host_rel",
        back_populates="hosted_events",
    )
    hosts_rel: sqlalchemy.orm.Mapped[list[EventHostRel]] = sqlalchemy.orm.relationship(
        "EventHostRel",
        back_populates="event",
    )
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
    )
    price: sqlalchemy.orm.Mapped[decimal.Decimal] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Numeric(10, 2),
        default=decimal.Decimal(0),
    )
    currency: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(3),
    )
    image_urls: sqlalchemy.orm.Mapped[list[str]] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ARRAY[str](sqlalchemy.Text),
        default=list,
    )
    games: sqlalchemy.orm.Mapped[list[Game]] = sqlalchemy.orm.relationship(
        "Game",
        back_populates="event",
    )

    participants_count: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.query_expression()  # type: ignore
    my_role: sqlalchemy.orm.Mapped[enums.EventParticipantRole] = (
        sqlalchemy.orm.query_expression()
    )  # type: ignore


class EventParticipantRel(base_models.BaseModel):
    __tablename__ = "event_participant_rel"

    event_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("event.id"),
        primary_key=True,
    )
    event: sqlalchemy.orm.Mapped[Event] = sqlalchemy.orm.relationship(
        "Event",
        back_populates="participants_rel",
    )
    player_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("player.id"),
        primary_key=True,
    )
    player: sqlalchemy.orm.Mapped[Player] = sqlalchemy.orm.relationship(
        "Player",
        back_populates="events_rel",
    )


class EventHostRel(base_models.BaseModel):
    __tablename__ = "event_host_rel"

    event_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("event.id"),
        primary_key=True,
    )
    event: sqlalchemy.orm.Mapped[Event] = sqlalchemy.orm.relationship(
        "Event",
        back_populates="hosts_rel",
    )
    user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("user.id"),
        primary_key=True,
    )
    user: sqlalchemy.orm.Mapped[User] = sqlalchemy.orm.relationship(
        "User",
        back_populates="hosted_events_rel",
    )
