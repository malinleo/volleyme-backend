from __future__ import annotations

import datetime
import typing
import uuid

import attrs

from src.common import entities as common_entities
from src.common import exc as common_exc
from src.volleyme.domain import exc, types


@attrs.define(kw_only=True)
class EventInvitation(common_entities.AggregateRoot):
    id: types.EventInvitationId = attrs.field(
        factory=lambda: types.EventInvitationId(uuid.uuid4()),
    )
    event_id: types.EventId
    user_id: types.UserId | None = None
    token: str
    expires_at: datetime.datetime | None = None
    used_at: datetime.datetime | None = None

    @property
    def is_expired(self) -> bool:
        return self.check_is_expired(datetime.datetime.now(datetime.UTC))

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @classmethod
    def create(
        cls,
        id: types.EventInvitationId,
        event_id: types.EventId,
        user_id: types.UserId | None,
        token: str,
        expires_at: datetime.datetime | None = None,
    ) -> typing.Self:
        current_dt = datetime.datetime.now(datetime.UTC)
        return cls(
            id=id,
            event_id=event_id,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=current_dt,
            updated_at=current_dt,
        )

    def check_is_expired(self, current_dt: datetime.datetime) -> bool:
        return self.expires_at is not None and self.expires_at < current_dt.astimezone(
            datetime.UTC,
        )

    def is_usable(
        self,
        event_id: types.EventId,
        user_id: types.UserId,
        use_dt: datetime.datetime,
    ) -> common_exc.ValidationResult[exc.DomainError]:
        errors: list[exc.DomainError] = []
        if self.event_id != event_id:
            errors.append(exc.EventInvitationNotForEventError())
        if self.user_id and self.user_id != user_id:
            errors.append(exc.EventInvitationNotForUserError())
        if self.is_used:
            errors.append(exc.EventInvitationUsedError())
        if self.check_is_expired(use_dt):
            errors.append(exc.EventInvitationExpiredError())
        if errors:
            return common_exc.ValidationResult(is_valid=False, errors=errors)
        return common_exc.ValidationResult(is_valid=True)

    def use(
        self,
        event_id: types.EventId,
        user_id: types.UserId,
        use_dt: datetime.datetime | None = None,
    ) -> None:
        use_dt = use_dt or datetime.datetime.now(datetime.UTC)
        validation_result = self.is_usable(event_id, user_id, use_dt)
        if not validation_result.is_valid:
            raise exc.DomainError.from_errors(validation_result.errors)
        self.used_at = use_dt
