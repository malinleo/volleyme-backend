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
    username: str = attrs.field(validator=attrs.validators.max_len(255))
    password_hash: PasswordHash
    created_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    profile: Profile | None = None

    @classmethod
    def create(
        cls,
        username: str,
        password_hash: PasswordHash,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        now = datetime.datetime.now(datetime.UTC)
        user = cls(
            id=types.UserId(uuid.uuid4()),
            username=username,
            password_hash=password_hash,
            created_at=now,
            updated_at=now,
        )
        user.profile = Profile(
            user=user,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            created_at=now,
            updated_at=now,
        )
        return user


@attrs.define(kw_only=True)
class Profile(common_entities.BaseEntity):
    """Profile entity."""

    user: User
    first_name: str | None = attrs.field(
        validator=attrs.validators.optional(attrs.validators.max_len(100)),
        default=None,
    )
    last_name: str | None = attrs.field(
        validator=attrs.validators.optional(attrs.validators.max_len(100)),
        default=None,
    )
    avatar_url: str | None = attrs.field(default=None)
    created_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
