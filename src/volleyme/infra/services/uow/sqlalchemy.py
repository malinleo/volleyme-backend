from __future__ import annotations

import dataclasses
import datetime
import logging
import typing

import sqlalchemy.ext.asyncio

from src.volleyme.application import services
from src.volleyme.infra.db import models, repos

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(kw_only=True)
class SQLAlchemyUOW(
    typing.Generic[services.uow.DepsT],
    services.uow.UOW[services.uow.DepsT],
):
    db_session: sqlalchemy.ext.asyncio.AsyncSession
    outbox_repo: repos.OutboxRepo

    async def commit(self) -> None:
        try:
            await self._save_events()
        except Exception as e:
            _logger.error(f"Error saving events: {e}")

        try:
            await self.db_session.commit()
        except Exception:
            await self.db_session.rollback()
            raise

    async def rollback(self) -> None:
        await self.db_session.rollback()

    async def _save_events(self) -> None:
        events_created_at = datetime.datetime.now(datetime.UTC)
        outbox_events = [
            models.Outbox(
                event_type=event.metadata.type,
                payload=event.payload,
                created_at=events_created_at,
                sent_at=None,
            )
            for event in self.events
        ]
        if outbox_events:
            await self.outbox_repo.create_outbox(outbox_events)
