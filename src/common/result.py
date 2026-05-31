import dataclasses
import typing

T = typing.TypeVar("T")
E = typing.TypeVar("E")


@dataclasses.dataclass(frozen=True)
class Ok(typing.Generic[T]):
    value: T


@dataclasses.dataclass(frozen=True)
class Err(typing.Generic[E]):
    errors: list[E]


Result: typing.TypeAlias = Ok[T] | Err[E]
