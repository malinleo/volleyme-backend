import datetime
import typing
import uuid

import pydantic

from src.common import schemas
from src.volleyme.domain import enums


class GetEventResponse(schemas.BaseSchema):
    id: uuid.UUID
    start_dt: datetime.datetime
    title: typing.Annotated[str, pydantic.Field(max_length=255)]
    description: str
    price: typing.Annotated[int, pydantic.Field(ge=0)]
    image_urls: list[str]


class CreateEventRequest(schemas.BaseSchema):
    start_dt: datetime.datetime
    title: typing.Annotated[str, pydantic.Field(max_length=255)]
    description: str
    price: typing.Annotated[int, pydantic.Field(ge=0)]
    image_urls: list[str]
    type: enums.GameType
