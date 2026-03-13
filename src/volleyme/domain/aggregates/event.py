from __future__ import annotations

import datetime
import decimal
import typing
import uuid

import attrs

from src.common import entities as common_entities
from src.volleyme.domain import enums, exc, types


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
    is_public: bool

    def __attrs_post_init__(self) -> None:
        self._validate_start_before_end()

    @property
    def is_finished(self) -> bool:
        return self.check_is_finished(datetime.datetime.now(datetime.UTC))

    @property
    def is_started(self) -> bool:
        return self.check_is_started(datetime.datetime.now(datetime.UTC))

    @classmethod
    def create(
        cls,
        title: str,
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
        game_type: enums.GameType,
        format_type: enums.EventFormatType,
        max_participants_count: int,
        country: str,
        city: str,
        address: str,
        description: str,
        price: decimal.Decimal,
        currency: str,
        image_urls: list[str],
        creator_user_id: types.UserId,
        is_public: bool,
    ) -> typing.Self:
        return cls(
            title=title,
            start_dt=start_dt.astimezone(datetime.UTC),
            end_dt=end_dt.astimezone(datetime.UTC),
            game_type=game_type,
            format_type=format_type,
            max_participants_count=max_participants_count,
            country=country,
            city=city,
            address=address,
            description=description,
            price=price,
            currency=currency,
            image_urls=image_urls,
            games=[],
            participants={creator_user_id},
            hosts={creator_user_id},
            created_by=creator_user_id,
            updated_by=creator_user_id,
            is_public=is_public,
        )

    def _validate_start_before_end(self) -> None:
        if self.start_dt >= self.end_dt:
            raise exc.EventEndBeforeStartError()

    def check_is_finished(self, current_dt: datetime.datetime) -> bool:
        return self.end_dt < current_dt.astimezone(datetime.UTC)

    def check_is_started(self, current_dt: datetime.datetime) -> bool:
        return self.start_dt < current_dt.astimezone(datetime.UTC)

    def is_user_host(self, user_id: types.UserId) -> bool:
        return user_id in self.hosts

    def is_user_participant(self, user_id: types.UserId) -> bool:
        return user_id in self.participants

    def is_visible_for_user(self, user_id: types.UserId) -> bool:
        return (
            self.is_public
            or self.is_user_host(user_id)
            or self.is_user_participant(user_id)
        )

    def add_participant(self, user_id: types.UserId) -> None:
        errors: list[exc.DomainError] = []
        if self.check_is_started(datetime.datetime.now(datetime.UTC)):
            errors.append(exc.EventAlreadyStartedError())
        if self.max_participants_count <= len(self.participants):
            errors.append(exc.EventAlreadyFullError())
        if self.is_user_participant(user_id):
            errors.append(exc.UserAlreadyParticipantError())
        if errors:
            raise exc.DomainError.from_errors(errors)
        self.participants.add(user_id)

    def remove_participant(self, user_id: types.UserId) -> None:
        errors: list[exc.DomainError] = []
        if self.check_is_started(datetime.datetime.now(datetime.UTC)):
            errors.append(exc.EventAlreadyStartedError())
        if not self.is_user_participant(user_id):
            errors.append(exc.UserNotParticipantError())
        if errors:
            raise exc.DomainError.from_errors(errors)
        self.participants.discard(user_id)

    def add_host(self, user_id: types.UserId) -> None:
        errors: list[exc.DomainError] = []
        if self.check_is_started(datetime.datetime.now(datetime.UTC)):
            errors.append(exc.EventAlreadyStartedError())
        if self.is_user_host(user_id):
            errors.append(exc.UserIsHostError())
        if errors:
            raise exc.DomainError.from_errors(errors)
        self.hosts.add(user_id)

    def remove_host(self, user_id: types.UserId) -> None:
        errors: list[exc.DomainError] = []
        if self.check_is_started(datetime.datetime.now(datetime.UTC)):
            errors.append(exc.EventAlreadyStartedError())
        if not self.is_user_host(user_id):
            errors.append(exc.UserNotHostError())
        if errors:
            raise exc.DomainError.from_errors(errors)
        self.hosts.discard(user_id)

    def make_public(
        self,
        user_id: types.UserId,
        current_dt: datetime.datetime,
    ) -> None:
        errors: list[exc.DomainError] = []
        if self.check_is_started(current_dt):
            errors.append(exc.EventAlreadyStartedError())
        if not self.is_user_host(user_id):
            errors.append(exc.UserNotHostError())
        if errors:
            raise exc.DomainError.from_errors(errors)
        self.is_public = True

    def make_private(
        self,
        user_id: types.UserId,
        current_dt: datetime.datetime,
    ) -> None:
        errors: list[exc.DomainError] = []
        if self.check_is_started(current_dt):
            errors.append(exc.EventAlreadyStartedError())
        if not self.is_user_host(user_id):
            errors.append(exc.UserNotHostError())
        if errors:
            raise exc.DomainError.from_errors(errors)
        self.is_public = False


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
