from __future__ import annotations

import enum


class ErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__ERROR__"
    REPO = "__REPO_ERROR__"
    REPO_NOT_FOUND = "__REPO_NOT_FOUND__"
    REPO_SAVE = "__REPO_SAVE_ERROR__"
    REPO_DELETE = "__REPO_DELETE_ERROR__"
    REPO_QUERY = "__REPO_QUERY_ERROR__"


class BaseError(Exception):
    """Base error with message."""

    default_msg: str = "Error occurred"
    code = ErrorCode.DEFAULT

    def __init__(
        self,
        msg: str | None = None,
        code: str | None = None,
        *args: object,
    ) -> None:
        self.msg = msg or self.default_msg
        self.code = code or self.code
        super().__init__(self.msg, *args)
