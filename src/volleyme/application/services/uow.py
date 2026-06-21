from __future__ import annotations

import abc
import dataclasses
import logging
import typing

from src.common import events as common_events
from src.common import schemas

_logger = logging.getLogger(__name__)

DepsT = typing.TypeVar("DepsT")


@dataclasses.dataclass(kw_only=True)
class UOW(typing.Generic[DepsT], abc.ABC):
    d: DepsT
    events: list[common_events.Event[schemas.BaseSchema]] = dataclasses.field(
        default_factory=list,
        init=False,
    )

    @abc.abstractmethod
    async def commit(self) -> None: ...

    @abc.abstractmethod
    async def rollback(self) -> None: ...

    def add_events(self, *events: common_events.Event[schemas.BaseSchema]) -> None:
        self.events.extend(events)
