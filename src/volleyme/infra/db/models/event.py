from __future__ import annotations

import typing
import sqlalchemy.orm
import datetime
from src.common.models import base as base_models
from src.volleyme.domain import enums

if typing.TYPE_CHECKING:
    from .game import Game


class Event(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "event"

    start_dt: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime,
    )
    title: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(255),
    )
    type: sqlalchemy.orm.Mapped[enums.GameType] = sqlalchemy.orm.mapped_column(
        sqlalchemy.SmallInteger,
    )
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
    )
    price: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Integer,
        default=0,
    )
    image_urls: sqlalchemy.orm.Mapped[list[str]] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ARRAY[str](sqlalchemy.Text),
        default=list,
    )
    games: sqlalchemy.orm.Mapped[list[Game]] = sqlalchemy.orm.relationship(
        "Game",
        back_populates="event",
    )
