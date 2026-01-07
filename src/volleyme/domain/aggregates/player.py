import datetime
import uuid

import attrs

from src.common import entities as common_entities
from src.volleyme.domain import enums, types


@attrs.define(kw_only=True)
class Player(common_entities.AggregateRoot):
    """Player aggregate root."""

    id: types.PlayerId = attrs.field(factory=lambda: types.PlayerId(uuid.uuid4()))
    type: enums.GameType
    user_id: types.UserId
    rating: int = attrs.field(validator=attrs.validators.ge(0))
    created_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
