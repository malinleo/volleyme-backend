from __future__ import annotations

import asyncio
import dataclasses
import logging
import threading

import orjson

from src.common import events, pubsub
from src.volleyme.application import services

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True)
class EventDispatcher:
    subscriber: pubsub.Subscriber[pubsub.ReceivedMessage]
    should_stop: threading.Event = threading.Event()

    async def run_in_thread(self) -> threading.Thread:
        thread = threading.Thread(target=asyncio.run, args=(self.run(),))
        thread.start()
        return thread

    async def run(self) -> None:
        async for message in await self.subscriber.iter_messages():
            if self.should_stop.is_set():
                break
            event_type: str | None = message.headers.get("event_type")
            if not event_type:
                _logger.warning(f"Message has no type header: {message.body!r}")
                continue
            value = services.events.handlers_registry.get(event_type)
            if not value:
                _logger.warning(f"Handler for event type {event_type} not found")
                continue
            event_schema_class, event_handler_factory = value
            event = event_schema_class.build(
                metadata=events.EventMetadata(type=event_type),
                payload=orjson.loads(message.body),
            )
            event_handler = await event_handler_factory()
            # TODO: move each handler to a separate thread
            try:
                await event_handler.handle(event)
            except Exception as e:
                _logger.error(f"Error handling event {event_type}: {e}")
                await message.reject()
                continue
            await message.ack()
