import sqlalchemy

from src.volleyme.infra.db import models

from . import base


class OutboxRepo(base.SQLAlchemyModelRepo):
    """Outbox repository implementation."""

    model_class = models.Outbox

    async def create_outbox(self, outbox_events: list[models.Outbox]) -> None:
        """Save outbox events."""
        await self._bulk_save(outbox_events, create=True)

    async def update_outbox(self, outbox_events: list[models.Outbox]) -> None:
        """Update outbox events."""
        await self._bulk_save(outbox_events, create=False)

    async def get_for_processing(self, limit: int, offset: int) -> list[models.Outbox]:
        """Get outbox events for processing."""
        subq = (
            sqlalchemy.select(self.model_class.id)
            .with_for_update(skip_locked=True)
            .where(
                self.model_class.sent_at.is_(None),
                self.model_class.processing_started_at.is_(None),
            )
            .order_by(self.model_class.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        query = (
            sqlalchemy.update(self.model_class)
            .where(self.model_class.id.in_(subq))
            .values(processing_started_at=sqlalchemy.func.now())
            .returning(self.model_class)
        )
        result = await self._try_execute(query)
        return list(result.result.scalars().unique().all())
