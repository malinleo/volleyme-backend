from __future__ import annotations

import asyncio
import logging

from dependency_injector import wiring

from src.common import pubsub
from src.config.settings import settings
from src.volleyme import di
from src.volleyme.application import services
from src.volleyme.domain import events as domain_events
from src.volleyme.infra.services import pubsub as infra_pubsub

from . import dispatcher

_logger = logging.getLogger(__name__)


def register_handlers(
    container: di.DI,
):
    services.events.handlers_registry.register(
        domain_events.types.EventType.EVENT_CREATED,
        (domain_events.EventCreated, container.services.event_created_handler),
    )


@wiring.inject
async def main(
    container: di.DI = wiring.Closing[wiring.Provide[di.DI.container]],
    subscriber: pubsub.Subscriber = wiring.Closing[
        wiring.Provide[di.DI.infra.event_subscriber]
    ],
    queue_binder: infra_pubsub.QueueBinder = wiring.Closing[
        wiring.Provide[di.DI.infra.queue_binder]
    ],
) -> None:
    register_handlers(container)
    await queue_binder.bind()
    disp = dispatcher.EventDispatcher(subscriber=subscriber)
    await disp.run()


if __name__ == "__main__":
    container = di.DI()
    container.wire(
        modules=[__name__],
        warn_unresolved=settings.DEBUG,
    )
    asyncio.run(main())
