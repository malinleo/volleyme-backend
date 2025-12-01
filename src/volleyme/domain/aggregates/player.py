import datetime
import typing
import uuid

import pydantic

from src.common import entities as common_entities
from src.volleyme.domain import enums, types


class Player(common_entities.AggregateRoot):
    """Player aggregate root."""

    id: typing.Annotated[
        types.PlayerId,
        pydantic.Field(default_factory=lambda: types.PlayerId(uuid.uuid4())),
    ]
    type: enums.GameType
    user_id: types.UserId
    rating: typing.Annotated[int, pydantic.Field(ge=0)]
    created_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(default_factory=lambda: datetime.datetime.now(datetime.UTC)),
    ]
    updated_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(default_factory=lambda: datetime.datetime.now(datetime.UTC)),
    ]
