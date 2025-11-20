from __future__ import annotations

import enum


class BaseError(Exception):
    """Base error with message."""

    default_msg: str = "Error occurred"

    def __init__(self, msg: str | None = None, *args: object) -> None:
        self.msg = msg or self.default_msg
        super().__init__(self.msg, *args)


class ErrorCode(enum.StrEnum):
    """All possible error codes."""

    REPO_ERROR = "__REPO_ERROR__"
    REPO_NOT_FOUND = "__REPO_NOT_FOUND__"
    REPO_SAVE = "__REPO_SAVE__"


ERROR_TEXTS: dict[ErrorCode, str] = {
    ErrorCode.REPO_ERROR: "Repository error",
    ErrorCode.REPO_NOT_FOUND: "Object with {object_data} wasn't found",
    ErrorCode.REPO_SAVE: "Object save error",
}
