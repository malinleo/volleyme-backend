from src.volleyme.domain import repos, types, aggregates
from src.common import repos as common_repos
from src.volleyme.infra.db import models


class EventRepo(
    common_repos.SQLAlchemyIdModelRepo,
    repos.EventRepo,
):
    """Event repository implementation."""

    _model_class = models.Event
    _default_joined_load_fields = frozenset(
        {models.Event.games, models.Game.teams, models.GameTeam.players},
    )

    async def get_event(self, event_id: types.EventId) -> aggregates.Event:
        return aggregates.Event.model_validate(
            await self._get_one(model_class=self._model_class, id=event_id)
        )

    async def get_events(self, limit: int, offset: int) -> list[aggregates.Event]:
        return [
            aggregates.Event.model_validate(event)
            for event in await self._get_many(
                model_class=self._model_class,
                where=(),
                order_by=(),
                limit=limit,
                offset=offset,
                joined_load_fields=self._default_joined_load_fields,
            )
        ]

    async def save_event(self, event: aggregates.Event) -> aggregates.Event:
        event_model = models.Event(
            id=event.id,
            start_dt=event.start_dt,
            title=event.title,
            description=event.description,
            price=event.price,
            image_urls=event.image_urls,
        )
        return aggregates.Event.model_validate(await self._save(event_model))

    async def delete_event(self, event_id: types.EventId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=event_id,
                model_class=self._model_class,
            ),
        )
