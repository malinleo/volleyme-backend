from __future__ import annotations

import datetime
import decimal
import typing
import uuid

import pydantic

from src.common import entities as common_entities
from src.volleyme.domain import enums, types


class Event(
    common_entities.TimeStampedEntity,
    common_entities.AggregateRoot,
):
    """Event aggregate root."""

    id: types.EventId = pydantic.Field(
        default_factory=lambda: types.EventId(uuid.uuid4())
    )
    created_by: types.UserId | None = None
    updated_by: types.UserId | None = None
    game_type: enums.GameType
    format_type: enums.EventFormatType
    country: str = pydantic.Field(max_length=255)
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    title: str = pydantic.Field(max_length=255)
    description: str
    price: decimal.Decimal = pydantic.Field(ge=0)
    currency: str = pydantic.Field(max_length=3)
    max_participants_count: int = pydantic.Field(gt=0)
    image_urls: list[str]
    games: list[Game]
    participants: list[types.UserId]
    hosts: list[types.UserId]

    @property
    def is_finished(self) -> bool:
        return self.check_is_finished(datetime.datetime.now(datetime.UTC))

    @pydantic.model_validator(mode="after")
    def check_start_before_end(self) -> typing.Self:
        if self.start_dt < self.end_dt:
            return self
        raise ValueError("Start date must be before end date")

    def check_is_finished(self, current_dt: datetime.datetime) -> bool:
        return self.end_dt < current_dt.astimezone(datetime.UTC)


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
