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


@dataclasses.dataclass(kw_only=True)
class ReceivedMessage:
    body: bytes
    headers: dict[str, typing.Any]


class Publisher(typing.Protocol):
    async def publish(
        self,
        messages: collections.abc.Iterable[Message],
    ) -> None: ...


class Subscriber(typing.Protocol):
    async def iter_messages(
        self,
    ) -> collections.abc.AsyncIterator[ReceivedMessage]: ...

    async def get_messages(
        self,
        count: int | None = None,
    ) -> list[ReceivedMessage]: ...


class AdminClient(typing.Protocol):
    async def purge(
        self,
        destination: Destination,
    ) -> None: ...


class Client(typing.Protocol):
    def build_publisher(
        self,
        destination: Destination,
    ) -> Publisher: ...

    def build_subscriber(
        self,
        destination: Destination,
    ) -> Subscriber: ...

    def build_admin(self) -> AdminClient: ...
