from __future__ import annotations

import dataclasses
import enum

from src.common import exc


class UseCaseErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__USE_CASE_ERROR__"
    VALIDATION_FAILED = "__USE_CASE_VALIDATION_FAILED__"
    NOT_FOUND = "__USE_CASE_NOT_FOUND__"
    UNAUTHORIZED = "__USE_CASE_UNAUTHORIZED__"
    PERMISSION_DENIED = "__USE_CASE_PERMISSION_DENIED__"
    PASSWORD_VALIDATION_FAILED = "__USE_CASE_PASSWORD_VALIDATION_FAILED__"
    USER_ALREADY_EXISTS = "__USER_ALREADY_EXISTS__"
    EXPIRED_TOKEN = "__EXPIRED_TOKEN__"
    REVOKED_TOKEN = "__REVOKED_TOKEN__"
    INVALID_TOKEN_TYPE = "__INVALID_TOKEN_TYPE__"
    INVALID_CREDENTIALS = "__INVALID_CREDENTIALS__"
    SESSION_INVALID = "__SESSION_INVALID__"


@dataclasses.dataclass
class UseCaseError(exc.BaseError):
    """Error in use case."""


class NotFound(UseCaseError):
    """Object wasn't found."""

    def __init__(self, message: str) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=UseCaseErrorCode.NOT_FOUND,
                    messages=[message],
                )
            ],
        )


class Unauthorized(UseCaseError):
    """Unauthorized."""

    def __init__(
        self,
        message: str | None = None,
        code: UseCaseErrorCode | None = None,
    ) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=code or UseCaseErrorCode.UNAUTHORIZED,
                    messages=[message or "Unauthorized"],
                )
            ],
        )


class PermissionDenied(UseCaseError):
    """Permission denied."""

    def __init__(self, message: str) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=UseCaseErrorCode.PERMISSION_DENIED,
                    messages=[message],
                )
            ],
        )
