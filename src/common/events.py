import typing

import attrs

PayloadT = typing.TypeVar("PayloadT", bound=attrs.AttrsInstance)


@attrs.define(frozen=True, kw_only=True)
class EventMetadata:
    type: str


@attrs.define(frozen=True, kw_only=True)
class Event(typing.Generic[PayloadT]):
    metadata: EventMetadata
    payload: PayloadT
