from __future__ import annotations

from src.common import entities as common_entities
from src.volleyme.domain import enums, types
import typing
import uuid
import datetime
import pydantic


class Event(common_entities.AggregateRoot):
    """Event aggregate root."""

    id: types.EventId = pydantic.Field(
        default_factory=lambda: types.EventId(uuid.uuid4())
    )
    start_dt: datetime.datetime
    title: typing.Annotated[str, pydantic.Field(max_length=255)]
    description: str
    price: typing.Annotated[int, pydantic.Field(ge=0)]
    image_urls: list[str]
    games: list[Game]
    type: enums.GameType
    created_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class Game(common_entities.BaseEntity):
    """Game entity."""

    event: Event
    type: enums.GameType
    type_info: dict[str, typing.Any]
    teams: list[GameTeam]


class GameTeam(common_entities.BaseEntity):
    """Game team entity."""

    game: Game
    title: typing.Annotated[str, pydantic.Field(max_length=100)]
    score: int
    players: list[types.PlayerId]
