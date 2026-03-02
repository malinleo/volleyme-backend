from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class FieldErrorDetail:
    code: str
    messages: list[str]


@dataclasses.dataclass(frozen=True)
class ErrorDetail:
    code: str
    messages: list[str] | None = None
    fields: dict[str, FieldErrorDetail] | None = None


class BaseError(Exception):
    """Base error with message."""

    def __init__(
        self,
        detail: ErrorDetail,
    ) -> None:
        self.detail = detail
        super().__init__(self.detail.code)
