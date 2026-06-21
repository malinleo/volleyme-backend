import collections.abc
import threading
import typing

from src.common import events, registry


class EventHandler(typing.Protocol):
    async def handle(
        self,
        event: events.Event[typing.Any],
    ) -> None: ...


class OutboxWorkerProtocol(typing.Protocol):
    async def run(self) -> None: ...
    async def run_in_thread(self) -> threading.Thread | None: ...


HandlerFactory = typing.Callable[[], collections.abc.Awaitable[EventHandler]]

handlers_registry: registry.RegistryProtocol[
    str,
    tuple[
        type[events.Event[typing.Any]],
        HandlerFactory,
    ],
] = registry.Registry()
