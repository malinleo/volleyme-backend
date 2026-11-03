import datetime
import decimal
import uuid

import pydantic

from src.common import schemas
from src.volleyme.domain import enums


class EventDetailResponse(schemas.BaseSchema):
    id: uuid.UUID
    title: str = pydantic.Field(max_length=255)
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    participants_count: int = pydantic.Field(gt=0)
    max_participants_count: int = pydantic.Field(gt=0)
    my_role: enums.EventParticipantRole
    price: decimal.Decimal = pydantic.Field(ge=0)
    currency: str = pydantic.Field(max_length=3)
    description: str
    participants: list[EventParticipantResponse]
    hosts: list[EventParticipantResponse]
    is_public: bool

    image_urls: list[str]
    country: str = pydantic.Field(max_length=2)
    game_type: enums.GameType
    format_type: enums.EventFormatType


class EventParticipantResponse(schemas.BaseSchema):
    id: uuid.UUID
    avatar_url: str | None
    name: str | None


class EventListResponse(schemas.BaseSchema):
    id: uuid.UUID
    title: str = pydantic.Field(max_length=255)
    start_dt: datetime.datetime
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    price: decimal.Decimal = pydantic.Field(ge=0)
    participants_count: int = pydantic.Field(gt=0)
    max_participants_count: int = pydantic.Field(gt=0)
    my_role: enums.EventParticipantRole
    is_public: bool

    image_urls: list[str]
    country: str = pydantic.Field(max_length=2)
    currency: str = pydantic.Field(max_length=3)
    game_type: enums.GameType


class CreateEventRequest(schemas.BaseSchema):
    title: str = pydantic.Field(max_length=255)
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    city: str = pydantic.Field(max_length=255)
    address: str = pydantic.Field(max_length=1024)
    max_participants_count: int = pydantic.Field(gt=0)
    price: decimal.Decimal = pydantic.Field(ge=0)
    description: str
    is_public: bool = pydantic.Field(default=True)

    # Auto filled for now
    image_urls: list[str] = pydantic.Field(default_factory=list)
    country: str = pydantic.Field(max_length=2, default="RU")
    currency: str = pydantic.Field(max_length=3, default="RUB")
    game_type: enums.GameType = enums.GameType.VOLLEYBALL
    format_type: enums.EventFormatType = enums.EventFormatType.DEFAULT


class ChangePrivacyRequest(schemas.BaseSchema):
    is_public: bool
