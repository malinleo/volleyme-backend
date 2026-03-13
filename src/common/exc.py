from __future__ import annotations

import collections.abc
import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class FieldErrorDetail:
    code: str
    messages: list[str]


@dataclasses.dataclass(frozen=True)
class ErrorDetail:
    code: str
    messages: list[str] | None = None
    fields: dict[str, FieldErrorDetail] | None = None


@dataclasses.dataclass
class BaseError(Exception):
    """Base error with message."""

    details: collections.abc.Sequence[ErrorDetail]

    def __init__(
        self,
        details: collections.abc.Sequence[ErrorDetail],
    ) -> None:
        self.details = details
        super().__init__(", ".join(detail.code for detail in details))

    @classmethod
    def from_errors(cls, errors: collections.abc.Iterable[BaseError]) -> BaseError:
        details = []
        for error in errors:
            details.extend(error.details)
        return cls(details=details)

    @classmethod
    def from_error(cls, error: BaseError) -> BaseError:
        return cls(details=error.details)


ErrorT = typing.TypeVar("ErrorT", bound=BaseError)


@dataclasses.dataclass
class ValidationResult(typing.Generic[ErrorT]):
    is_valid: bool
    errors: list[ErrorT] = dataclasses.field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid
