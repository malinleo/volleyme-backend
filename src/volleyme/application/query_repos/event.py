import typing

from src.volleyme.application import dto
from src.volleyme.domain import types


class EventQueryRepo(typing.Protocol):
    """Event repository protocol."""

    async def get_event_info_for_user(
        self,
        event_id: types.EventId,
        user_id: types.UserId,
    ) -> dto.EventDetailsDto | None:
        """Get event info for user by id."""
        ...

    async def get_events_info_for_user(
        self,
        user_id: types.UserId,
        limit: int,
        offset: int,
        only_my_events: bool = ...,
    ) -> list[dto.EventListDto]:
        """Get events info."""
        ...
