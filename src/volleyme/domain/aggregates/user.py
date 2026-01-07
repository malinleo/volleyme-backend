from __future__ import annotations

import datetime
import uuid

import attrs

from src.common import entities as common_entities
from src.volleyme.domain import types


@attrs.define(kw_only=True)
class PasswordHash(common_entities.ValueObject):
    """Password hash value object."""

    value: str


@attrs.define(kw_only=True)
class User(common_entities.AggregateRoot):
    """User aggregate root."""

    id: types.UserId = attrs.field(factory=lambda: types.UserId(uuid.uuid4()))
    email: str = attrs.field(validator=common_entities.validators.is_email)
    password_hash: PasswordHash
    created_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    profile: Profile | None = None


@attrs.define(kw_only=True)
class Profile(common_entities.BaseEntity):
    """Profile entity."""

    user: User
    first_name: str = attrs.field(validator=attrs.validators.max_len(100))
    last_name: str = attrs.field(validator=attrs.validators.max_len(100))
    avatar_url: str
    created_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
