import asyncio
import logging

from dependency_injector import wiring

from src.common import pubsub
from src.config import settings
from src.volleyme import di
from src.volleyme.application import services
from src.volleyme.domain import events as domain_events

from .outbox_worker import OutboxWorker, OutboxWorkerDeps

_logger = logging.getLogger(__name__)


@wiring.inject
def register_handlers(
    container: di.DI = wiring.Closing[wiring.Provide[di.DI.container]],
):
    services.events.handlers_registry.register(
        domain_events.types.EventType.EVENT_CREATED,
        (domain_events.EventCreated, container.services.event_created_handler),
    )


@wiring.inject
async def main(
    outbox_worker_uow: services.uow.UOW[OutboxWorkerDeps] = wiring.Closing[
        wiring.Provide[di.DI.usecases.uow.outbox_worker_uow]
    ],
    outbox_publisher: pubsub.Publisher = wiring.Closing[
        wiring.Provide[di.DI.infra.outbox_publisher]
    ],
) -> None:
    outbox_worker = OutboxWorker(
        uow=outbox_worker_uow,
        publisher=outbox_publisher,
        small_poll_interval=settings.OUTBOX_SMALL_POLL_INTERVAL_SECONDS,
        big_poll_interval=settings.OUTBOX_BIG_POLL_INTERVAL_SECONDS,
        poll_batch_size=settings.OUTBOX_POLL_BATCH_SIZE,
    )
    await outbox_worker.run()


if __name__ == "__main__":
    container = di.DI()
    container.wire(
        modules=[__name__],
        warn_unresolved=settings.DEBUG,
    )
    asyncio.run(main())
