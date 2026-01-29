from __future__ import annotations

import datetime
import decimal
import typing
import uuid

import attrs

from src.common import entities as common_entities
from src.volleyme.domain import enums, types


@attrs.define(kw_only=True)
class Event(
    common_entities.TimeStampedEntity,
    common_entities.AggregateRoot,
):
    """Event aggregate root."""

    id: types.EventId = attrs.field(factory=lambda: types.EventId(uuid.uuid4()))
    created_by: types.UserId | None = None
    updated_by: types.UserId | None = None
    game_type: enums.GameType
    format_type: enums.EventFormatType
    country: str = attrs.field(validator=attrs.validators.max_len(255))
    city: str = attrs.field(validator=attrs.validators.max_len(255))
    address: str = attrs.field(validator=attrs.validators.max_len(1024))
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    title: str = attrs.field(validator=attrs.validators.max_len(255))
    description: str
    price: decimal.Decimal = attrs.field(
        validator=attrs.validators.ge(decimal.Decimal(0)),
    )
    currency: str = attrs.field(validator=attrs.validators.max_len(3))
    max_participants_count: int = attrs.field(validator=attrs.validators.gt(0))
    image_urls: list[str]
    games: list[Game]
    participants: set[types.UserId]
    hosts: set[types.UserId]

    def __attrs_post_init__(self) -> None:
        errors = []
        if error := self._validate_start_before_end():
            errors.append(error)
        if errors:
            raise ValueError(errors)

    @property
    def is_finished(self) -> bool:
        return self.check_is_finished(datetime.datetime.now(datetime.UTC))

    @property
    def is_started(self) -> bool:
        return self.check_is_started(datetime.datetime.now(datetime.UTC))

    def _validate_start_before_end(self) -> Exception | None:
        if self.start_dt >= self.end_dt:
            return ValueError("Start date must be before end date")
        return None

    def check_is_finished(self, current_dt: datetime.datetime) -> bool:
        return self.end_dt < current_dt.astimezone(datetime.UTC)

    def check_is_started(self, current_dt: datetime.datetime) -> bool:
        return self.start_dt < current_dt.astimezone(datetime.UTC)

    def add_participant(self, user_id: types.UserId) -> None:
        self.participants.add(user_id)

    def remove_participant(self, user_id: types.UserId) -> None:
        self.participants.discard(user_id)

    def add_host(self, user_id: types.UserId) -> None:
        self.hosts.add(user_id)

    def remove_host(self, user_id: types.UserId) -> None:
        self.hosts.discard(user_id)


@attrs.define(kw_only=True)
class Game(common_entities.BaseEntity):
    """Game entity."""

    event: Event
    type: enums.GameType
    type_info: dict[str, typing.Any]
    teams: list[GameTeam]


@attrs.define(kw_only=True)
class GameTeam(common_entities.BaseEntity):
    """Game team entity."""

    game: Game
    title: str = attrs.field(validator=attrs.validators.max_len(100))
    score: int
    players: list[types.PlayerId]
