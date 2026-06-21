from __future__ import annotations

import dataclasses

from src.volleyme.application import services
from src.volleyme.domain import events as domain_events
from src.volleyme.domain import repos


@dataclasses.dataclass(kw_only=True)
class EventCreatedHandlerDeps:
    event_repo: repos.EventRepo


@dataclasses.dataclass(kw_only=True)
class EventCreatedHandler(services.events.EventCreatedHandlerProtocol):
    uow: services.uow.UOW[EventCreatedHandlerDeps]

    async def handle(self, event: domain_events.EventCreated) -> None:
        print("Event created: ", event)
