from __future__ import annotations

import collections.abc
import dataclasses
import typing


@dataclasses.dataclass(kw_only=True)
class Destination:
    name: str


class Message(typing.Protocol):
    def get_body(self) -> bytes: ...
    def get_headers(self) -> dict[str, typing.Any]: ...
    def get_routing_key(self) -> str: ...


class ReceivedMessage(typing.Protocol):
    body: bytes
    headers: dict[str, typing.Any]

    async def ack(self) -> None: ...
    async def reject(self, requeue: bool = False) -> None: ...


ReceivedMessageT = typing.TypeVar("ReceivedMessageT", bound=ReceivedMessage)


class Publisher(typing.Protocol):
    async def publish(
        self,
        messages: collections.abc.Iterable[Message],
    ) -> None: ...


class Subscriber(typing.Protocol[ReceivedMessageT]):
    async def iter_messages(
        self,
    ) -> collections.abc.AsyncIterator[ReceivedMessageT]: ...

    async def get_messages(
        self,
        count: int | None = None,
    ) -> list[ReceivedMessageT]: ...


class AdminClient(typing.Protocol):
    async def purge(
        self,
        destination: Destination,
    ) -> None: ...
