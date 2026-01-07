import datetime
import typing

import attrs


@attrs.define(kw_only=True)
class BaseEntity:
    """Base class for domain entities."""


@attrs.define(kw_only=True)
class TimeStampedEntity(BaseEntity):
    """Base class for domain entities with create and update timestamps."""

    created_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = attrs.field(
        factory=lambda: datetime.datetime.now(datetime.UTC)
    )


@attrs.define(kw_only=True)
class AggregateRoot(BaseEntity):
    """Base class for domain aggregate roots."""


@attrs.define(kw_only=True)
class ValueObject:
    """Base class for domain value objects."""


BaseEntityT = typing.TypeVar("BaseEntityT", bound=BaseEntity)
AggregateRootT = typing.TypeVar("AggregateRootT", bound=AggregateRoot)
ValueObjectT = typing.TypeVar("ValueObjectT", bound=ValueObject)
