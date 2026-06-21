from __future__ import annotations

import dataclasses
import logging

import orjson

from src.common import events, pubsub
from src.volleyme.application import services

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True)
class EventDispatcher:
    subscriber: pubsub.Subscriber

    async def run(self) -> None:
        async for message in await self.subscriber.iter_messages():
            event_type: str | None = message.headers.get("type")
            if not event_type:
                _logger.warning(f"Message has no type header: {message.body!r}")
                return
            value = services.events.handlers_registry.get(event_type)
            if not value:
                _logger.warning(f"Handler for event type {event_type} not found")
                return
            event_schema_class, event_handler_factory = value
            event = event_schema_class.build(
                metadata=events.EventMetadata(type=event_type),
                payload=orjson.loads(message.body),
            )
            event_handler = await event_handler_factory()
            await event_handler.handle(event)
