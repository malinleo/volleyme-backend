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

    def __init__(self, message: str) -> None:
        super().__init__(
            details=[
                exc.ErrorDetail(
                    code=UseCaseErrorCode.UNAUTHORIZED,
                    messages=[message],
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
