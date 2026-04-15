from __future__ import annotations

import datetime
import uuid

import attrs

from src.common import entities as common_entities
from src.volleyme.domain import types


@attrs.define(kw_only=True)
class UserSession(
    common_entities.AggregateRoot,
    common_entities.TimeStampedEntity,
):
    """User session aggregate root."""

    id: types.UserSessionId = attrs.field(
        factory=lambda: types.UserSessionId(uuid.uuid4()),
    )
    user_id: types.UserId
    expires_at: datetime.datetime
    revoked_at: datetime.datetime | None = None

    @classmethod
    def create(
        cls,
        user_id: types.UserId,
        expires_at: datetime.datetime,
    ) -> UserSession:
        now = datetime.datetime.now(datetime.UTC)
        return cls(
            id=types.UserSessionId(uuid.uuid4()),
            user_id=user_id,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
        )

    def revoke(self, now: datetime.datetime | None = None) -> None:
        if self.is_revoked():
            return
        now = now or datetime.datetime.now(datetime.UTC)
        self.revoked_at = now
        self.updated_at = now

    def is_expired(self, now: datetime.datetime | None = None) -> bool:
        now = now or datetime.datetime.now(datetime.UTC)
        return self.expires_at < now

    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_valid(self, now: datetime.datetime | None = None) -> bool:
        now = now or datetime.datetime.now(datetime.UTC)
        return not self.is_expired(now) and not self.is_revoked()
