from src.common import entities as common_entities
import typing
import uuid
import datetime
import pydantic
from src.volleyme.domain import types


class User(common_entities.AggregateRoot):
    """User aggregate root."""

    email: pydantic.EmailStr
    password: str
    id: typing.Annotated[
        types.UserId,
        pydantic.Field(default_factory=lambda: types.UserId(uuid.uuid4())),
    ]
    created_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(default_factory=datetime.datetime.now),
    ]
    updated_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(default_factory=datetime.datetime.now),
    ]


class Profile(common_entities.BaseEntity):
    """Profile entity."""

    user: User
    first_name: typing.Annotated[
        str,
        pydantic.Field(max_length=100),
    ]
    last_name: typing.Annotated[
        str,
        pydantic.Field(max_length=100),
    ]
    avatar_url: pydantic.FileUrl
    created_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(default_factory=datetime.datetime.now),
    ]
    updated_at: typing.Annotated[
        datetime.datetime,
        pydantic.Field(default_factory=datetime.datetime.now),
    ]
