from __future__ import annotations

import datetime
import uuid
from collections.abc import Generator
from contextlib import contextmanager

import pydantic

from src.common import entities as common_entities
from src.volleyme.domain import types


def is_recursion_validation_error(exc: pydantic.ValidationError) -> bool:
    errors = exc.errors()
    return len(errors) == 1 and errors[0]["type"] == "recursion_loop"


@contextmanager
def suppress_recursion_validation_error() -> Generator[None]:
    try:
        yield
    except pydantic.ValidationError as exc:
        if not is_recursion_validation_error(exc):
            raise exc


class User(common_entities.AggregateRoot):
    """User aggregate root."""

    email: pydantic.EmailStr
    password: str
    id: types.UserId = pydantic.Field(
        default_factory=lambda: types.UserId(uuid.uuid4()),
    )
    created_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    profile: Profile | None = None


class Profile(common_entities.BaseEntity):
    """Profile entity."""

    user: User
    first_name: str = pydantic.Field(max_length=100)
    last_name: str = pydantic.Field(max_length=100)
    avatar_url: str
    created_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
