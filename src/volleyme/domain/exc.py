import datetime
import enum

from src.common import exc


class ErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "DOMAIN_ERROR"
    EVENT_END_BEFORE_START = "EVENT_END_BEFORE_START"


class DomainError(exc.BaseError):
    """Error in domain."""


class EventEndBeforeStartError(DomainError):
    """Error in event end before start."""

    def __init__(self, start_dt: datetime.datetime, end_dt: datetime.datetime) -> None:
        super().__init__(
            detail=exc.ErrorDetail(
                code=ErrorCode.EVENT_END_BEFORE_START,
                fields={
                    "start_dt": exc.FieldErrorDetail(
                        code=ErrorCode.EVENT_END_BEFORE_START,
                        messages=["Event end date must be after start date"],
                    ),
                },
            )
        )
