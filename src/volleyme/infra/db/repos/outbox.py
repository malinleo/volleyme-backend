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

    async def get_outbox_events(self, limit: int, offset: int) -> list[models.Outbox]:
        """Get outbox events."""
        outbox_events, _ = await self._get_many(
            model_class=self.model_class,
            where=(self.model_class.sent_at.is_(None),),
            order_by=(),
            limit=limit,
            offset=offset,
        )
        return list(outbox_events)
