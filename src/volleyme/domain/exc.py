from __future__ import annotations

import dataclasses
import enum

from src.common import exc


class ErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "DOMAIN_ERROR"
    EVENT_END_BEFORE_START = "EVENT_END_BEFORE_START"
    EVENT_ALREADY_STARTED = "EVENT_ALREADY_STARTED"
    EVENT_INVITATION_EXPIRED = "EVENT_INVITATION_EXPIRED"
    EVENT_INVITATION_USED = "EVENT_INVITATION_USED"
    EVENT_INVITATION_NOT_FOR_USER = "EVENT_INVITATION_NOT_FOR_USER"
    EVENT_INVITATION_NOT_FOR_EVENT = "EVENT_INVITATION_NOT_FOR_EVENT"
    EVENT_ALREADY_FULL = "EVENT_ALREADY_FULL"
    USER_ALREADY_PARTICIPANT = "USER_ALREADY_PARTICIPANT"
    USER_NOT_PARTICIPANT = "USER_NOT_PARTICIPANT"
    USER_IS_HOST = "USER_IS_HOST"
    USER_NOT_HOST = "USER_NOT_HOST"


@dataclasses.dataclass
class DomainError(exc.BaseError):
    """Error in domain."""


class EventEndBeforeStartError(DomainError):
    """Error in event end before start."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_END_BEFORE_START,
                    messages=["Event end date must be after start date"],
                    fields={
                        "start_dt": exc.FieldErrorDetail(
                            code=ErrorCode.EVENT_END_BEFORE_START,
                            messages=["Event end date must be after start date"],
                        ),
                        "end_dt": exc.FieldErrorDetail(
                            code=ErrorCode.EVENT_END_BEFORE_START,
                            messages=["Event end date must be after start date"],
                        ),
                    },
                )
            ]
        )


class EventAlreadyStartedError(DomainError):
    """Action performed on an event that is already started."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_ALREADY_STARTED,
                    messages=["Event already started"],
                )
            ]
        )


class EventInvitationExpiredError(DomainError):
    """Event invitation expired."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_INVITATION_EXPIRED,
                    messages=["Event invitation expired"],
                )
            ]
        )


class EventInvitationUsedError(DomainError):
    """Event invitation already used."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_INVITATION_USED,
                    messages=["Event invitation already used"],
                )
            ]
        )


class EventInvitationNotForUserError(DomainError):
    """Event invitation not for given user."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_INVITATION_NOT_FOR_USER,
                    messages=["Event invitation not for given user"],
                )
            ]
        )


class EventInvitationNotForEventError(DomainError):
    """Event invitation not for given event."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_INVITATION_NOT_FOR_EVENT,
                    messages=["Event invitation not for given event"],
                )
            ]
        )


class EventAlreadyFullError(DomainError):
    """Event already full."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.EVENT_ALREADY_FULL,
                    messages=["Event is already full"],
                )
            ]
        )


class UserAlreadyParticipantError(DomainError):
    """User already participant."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.USER_ALREADY_PARTICIPANT,
                    messages=["User is already a participant of the event"],
                )
            ]
        )


class UserNotParticipantError(DomainError):
    """User not participant."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.USER_NOT_PARTICIPANT,
                    messages=["User is not a participant of the event"],
                )
            ]
        )


class UserIsHostError(DomainError):
    """User is host."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.USER_IS_HOST,
                    messages=["User is a host of the event"],
                )
            ]
        )


class UserNotHostError(DomainError):
    """User not host."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=ErrorCode.USER_NOT_HOST,
                    messages=["User is not a host of the event"],
                )
            ]
        )
