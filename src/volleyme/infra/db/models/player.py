from __future__ import annotations

import typing
import uuid

import sqlalchemy
import sqlalchemy.orm

from src.common.models import base as base_models
from src.volleyme.domain import enums

if typing.TYPE_CHECKING:
    from .user import User


class Player(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "player"

    type: sqlalchemy.orm.Mapped[enums.GameType] = sqlalchemy.orm.mapped_column(
        sqlalchemy.SmallInteger,
    )
    user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("user.id", name="fk_player_user_id"),
    )
    user: sqlalchemy.orm.Mapped[User] = sqlalchemy.orm.relationship(
        "User",
    )
    rating: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        default=0,
    )
