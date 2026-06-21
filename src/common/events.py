from __future__ import annotations

import abc
import typing

from . import schemas

PayloadT = typing.TypeVar("PayloadT", bound=schemas.BaseSchema)


class EventMetadata(schemas.BaseSchema):
    type: str


class Event(schemas.BaseSchema, typing.Generic[PayloadT], abc.ABC):
    metadata: EventMetadata
    payload: PayloadT

    @classmethod
    @abc.abstractmethod
    def build(
        cls,
        metadata: EventMetadata,
        payload: dict[str, typing.Any],
    ) -> Event[PayloadT]: ...
