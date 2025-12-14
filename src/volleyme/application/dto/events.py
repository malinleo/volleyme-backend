import datetime
import decimal
import uuid

import pydantic

from src.common import dto
from src.volleyme.domain import enums


class CreateEventDto(dto.BaseDto):
    title: str = pydantic.Field(max_length=255)
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    max_participants_count: int = pydantic.Field(gt=0)
    price: decimal.Decimal = pydantic.Field(ge=0)
    currency: str = pydantic.Field(max_length=3)
    description: str
    image_urls: list[str]
    country: str = pydantic.Field(max_length=2)
    game_type: enums.GameType
    format_type: enums.EventFormatType


class ParticipantInfoDto(dto.BaseDto):
    id: uuid.UUID
    avatar_url: str | None
    name: str | None


class EventListDto(dto.BaseDto):
    id: uuid.UUID
    title: str = pydantic.Field(max_length=255)
    start_dt: datetime.datetime
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    price: decimal.Decimal = pydantic.Field(ge=0)
    participants_count: int = pydantic.Field(gt=0)

    image_urls: list[str]
    country: str = pydantic.Field(max_length=2)
    currency: str = pydantic.Field(max_length=3)
    game_type: enums.GameType


class EventDetailsDto(dto.BaseDto):
    id: uuid.UUID
    title: str = pydantic.Field(max_length=255)
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    participants_count: int
    max_participants_count: int = pydantic.Field(gt=0)
    price: decimal.Decimal = pydantic.Field(ge=0)
    currency: str = pydantic.Field(max_length=3)
    description: str
    image_urls: list[str]
    country: str = pydantic.Field(max_length=2)
    game_type: enums.GameType
    format_type: enums.EventFormatType
    participants: list[ParticipantInfoDto]
    hosts: list[ParticipantInfoDto]
