import datetime
import typing

import pydantic

from src.common import dto
from src.volleyme.domain import enums


class CreateEventDto(dto.BaseDto):
    start_dt: datetime.datetime
    title: typing.Annotated[str, pydantic.Field(max_length=255)]
    description: str
    price: typing.Annotated[int, pydantic.Field(ge=0)]
    image_urls: list[str]
    type: enums.GameType
