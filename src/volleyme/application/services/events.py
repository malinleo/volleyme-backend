import collections.abc
import typing

from src.common import events


class EventDispatcher(typing.Protocol):
    async def dispatch(
        self,
        events: collections.abc.Sequence[events.Event[typing.Any]],
    ) -> None: ...
