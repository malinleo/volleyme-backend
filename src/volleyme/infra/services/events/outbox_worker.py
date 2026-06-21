import asyncio
import dataclasses
import datetime
import logging
import threading
import typing

import orjson

from src.common import pubsub, schemas
from src.config import settings
from src.volleyme.application import services
from src.volleyme.domain.repos import exc as repos_exc
from src.volleyme.infra.db import repos

_logger = logging.getLogger(__name__)


class OutboxMessageHeaders(schemas.BaseSchema):
    event_type: str
    created_at: datetime.datetime
    sent_at: datetime.datetime
    id: str
    trace_id: str


@dataclasses.dataclass(kw_only=True)
class OutboxWorkerDeps:
    outbox_repo: repos.OutboxRepo


@dataclasses.dataclass(kw_only=True)
class OutboxMessage(pubsub.Message):
    body: dict[str, typing.Any]
    headers: OutboxMessageHeaders

    def get_body(self) -> bytes:
        return orjson.dumps(self.body)

    def get_headers(self) -> dict[str, typing.Any]:
        return self.headers.model_dump(mode="json")

    def get_routing_key(self) -> str:
        return settings.OUTBOX_ROUTING_KEY


@dataclasses.dataclass(kw_only=True)
class OutboxWorker(services.events.OutboxWorkerProtocol):
    uow: services.uow.UOW[OutboxWorkerDeps]
    publisher: pubsub.Publisher
    should_stop: threading.Event = threading.Event()
    small_poll_interval: float
    big_poll_interval: float
    poll_batch_size: int

    def run_in_thread(self) -> threading.Thread:
        thread = threading.Thread(target=asyncio.run, args=(self.run(),))
        thread.start()
        return thread

    async def run(self) -> None:
        _logger.info("Starting outbox worker")
        while not self.should_stop.is_set():
            try:
                events = await self.uow.d.outbox_repo.get_for_processing(
                    limit=self.poll_batch_size,
                    offset=0,
                )
            except repos_exc.RepoError as e:
                _logger.error(f"Error getting outbox events: {e}")
                await asyncio.sleep(self.big_poll_interval)
                continue
            if not events:
                await asyncio.sleep(self.big_poll_interval)
                continue
            send_dt = datetime.datetime.now(datetime.UTC)
            for event in events:
                event.sent_at = send_dt

            messages = [
                OutboxMessage(
                    body=event.payload,
                    headers=OutboxMessageHeaders(
                        event_type=event.event_type,
                        created_at=event.created_at,
                        sent_at=send_dt,
                        id=str(event.id),
                        trace_id=str(event.id),
                    ),
                )
                for event in events
            ]
            try:
                await self.publisher.publish(messages)
            except Exception as e:
                for event in events:
                    event.sent_at = None
                    event.processing_started_at = None
                    event.last_error = str(e)
                try:
                    await self.uow.d.outbox_repo.update_outbox(events)
                except repos_exc.RepoError as repo_error:
                    _logger.error(
                        f"Error updating outbox events after publishing error:\n{e}\nRepo error:\n{repo_error}",
                        exc_info=True,
                    )
                    raise
                _logger.error(f"Error publishing events: {e}", exc_info=True)
                raise

            await self.uow.d.outbox_repo.update_outbox(events)
            await self.uow.commit()
            await asyncio.sleep(self.small_poll_interval)
        _logger.info("Outbox worker stopped")
