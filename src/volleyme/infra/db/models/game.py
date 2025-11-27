from __future__ import annotations

import typing
import uuid
import sqlalchemy.orm
from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .event import Event
    from .game_team import GameTeam


class Game(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "game"

    event_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("event.id"),
    )
    event: sqlalchemy.orm.Mapped[Event] = sqlalchemy.orm.relationship(
        "Event",
        back_populates="games",
    )
    type: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(50),
    )
    type_info: sqlalchemy.orm.Mapped[dict[str, typing.Any]] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.JSON,
            default=dict,
        )
    )
    teams: sqlalchemy.orm.Mapped[list[GameTeam]] = sqlalchemy.orm.relationship(
        "GameTeam",
        back_populates="game",
    )
