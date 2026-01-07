from __future__ import annotations

import enum
import typing


class ErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__ERROR__"
    REPO = "__REPO_ERROR__"
    REPO_NOT_FOUND = "__REPO_NOT_FOUND__"
    REPO_SAVE = "__REPO_SAVE_ERROR__"
    REPO_DELETE = "__REPO_DELETE_ERROR__"
    REPO_QUERY = "__REPO_QUERY_ERROR__"


class ErrorDetail(typing.NamedTuple):
    message: str
    code: str | None = None


class BaseError(Exception):
    """Base error with message."""

    default_msg: str = "Error occurred"
    code = ErrorCode.DEFAULT

    def __init__(
        self,
        details: list[ErrorDetail] | None = None,
        code: str | None = None,
        *args: object,
    ) -> None:
        if not details:
            details = [ErrorDetail(message=self.default_msg, code=code or self.code)]
        self.details = details
        super().__init__(self.details, *args)

    def build_details(self) -> list[dict[str, typing.Any]]:
        return [
            {"message": detail.message, "code": detail.code} for detail in self.details
        ]
