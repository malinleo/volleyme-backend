import datetime
import typing

import attrs

from src.common import events


class DomainEvent(events.Event[events.PayloadT]):
    """Base class for domain events."""


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
class AggregateRoot(TimeStampedEntity):
    """Base class for domain aggregate roots."""

    _events: list[DomainEvent] = attrs.field(factory=list, init=False)

    def add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events, self._events = self._events, []
        return events


@attrs.define(kw_only=True)
class ValueObject:
    """Base class for domain value objects."""


BaseEntityT = typing.TypeVar("BaseEntityT", bound=BaseEntity)
AggregateRootT = typing.TypeVar("AggregateRootT", bound=AggregateRoot)
ValueObjectT = typing.TypeVar("ValueObjectT", bound=ValueObject)
