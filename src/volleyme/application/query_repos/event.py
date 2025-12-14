import typing

from src.volleyme.application import dto
from src.volleyme.domain import types


class EventQueryRepo(typing.Protocol):
    """Event repository protocol."""

    async def get_event_info(
        self,
        event_id: types.EventId,
    ) -> dto.EventDetailsDto | None:
        """Get event info by id."""
        ...

    async def get_events_info(
        self,
        limit: int,
        offset: int,
    ) -> list[dto.EventListDto]:
        """Get events info."""
        ...
