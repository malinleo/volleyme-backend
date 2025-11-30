import typing
from src.volleyme.domain import types, aggregates


class EventRepo(typing.Protocol):
    """Event repository protocol."""

    async def get_event(self, event_id: types.EventId) -> aggregates.Event | None:
        """Get event by id."""
        ...

    async def get_events(self, limit: int, offset: int) -> list[aggregates.Event]:
        """Get list of events with pagination."""
        ...

    async def save_event(self, event: aggregates.Event) -> aggregates.Event:
        """Create event."""
        ...

    async def delete_event(self, event_id: types.EventId) -> None:
        """Delete event by id."""
        ...
