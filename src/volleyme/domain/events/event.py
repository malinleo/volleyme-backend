from __future__ import annotations

import datetime
import decimal
import typing

from src.common import entities, events, schemas
from src.volleyme.domain import enums, types


class EventCreatedPayload(schemas.BaseSchema):
    id: types.EventId
    title: str
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    city: str
    address: str
    max_participants_count: int
    price: decimal.Decimal
    currency: str
    description: str
    image_urls: list[str]
    country: str
    game_type: enums.GameType
    format_type: enums.EventFormatType
    is_public: bool
    participants: set[types.UserId]
    hosts: set[types.UserId]
    created_by: types.UserId
    updated_by: types.UserId


class EventCreated(entities.DomainEvent[EventCreatedPayload]):
    @classmethod
    def build(
        cls,
        metadata: events.EventMetadata,
        payload: dict[str, typing.Any],
    ) -> EventCreated:
        return cls(metadata=metadata, payload=EventCreatedPayload(**payload))
