import typing
import uuid

import sqlalchemy.orm

from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .game import Game


class GameTeam(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "game_team"

    game_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("game.id"),
    )
    game: sqlalchemy.orm.Mapped[Game] = sqlalchemy.orm.relationship(
        "Game",
        back_populates="teams",
    )
    title: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(100),
    )
    score: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        default=0,
    )
    players: sqlalchemy.orm.Mapped[list[uuid.UUID]] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ARRAY[uuid.UUID](sqlalchemy.UUID),
        default=list,
    )
