from __future__ import annotations

import dataclasses
import typing

from src.volleyme.application.services import uow
from src.volleyme.domain import events as domain_events
from src.volleyme.domain import repos

from . import base


@dataclasses.dataclass(kw_only=True)
class EventCreatedHandlerDeps:
    event_repo: repos.EventRepo


class EventCreatedHandlerProtocol(base.EventHandler, typing.Protocol):
    uow: uow.UOW[EventCreatedHandlerDeps]

    async def handle(self, event: domain_events.EventCreated) -> None: ...
