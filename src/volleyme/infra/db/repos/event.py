import sqlalchemy.orm

from src.common import repos as common_repos
from src.volleyme.domain import aggregates, repos, types
from src.volleyme.infra.db import models


class EventRepo(
    common_repos.SQLAlchemyIdModelRepo,
    repos.EventRepo,
):
    """Event repository implementation."""

    _model_class = models.Event

    def _parse_event_model(self, event_model: models.Event) -> aggregates.Event:
        event = aggregates.Event(
            id=types.EventId(event_model.id),
            start_dt=event_model.start_dt,
            title=event_model.title,
            type=event_model.type,
            description=event_model.description,
            price=event_model.price,
            image_urls=event_model.image_urls,
            games=[],
        )
        for game_model in event_model.games:
            game = aggregates.Game(
                event=event,
                type=game_model.type,
                type_info=game_model.type_info,
                teams=[],
            )
            for team_model in game_model.teams:
                team = aggregates.GameTeam(
                    game=game,
                    title=team_model.title,
                    score=team_model.score,
                    players=[
                        types.PlayerId(player_id) for player_id in team_model.players
                    ],
                )
                game.teams.append(team)
            event.games.append(game)
        return event

    async def get_event(self, event_id: types.EventId) -> aggregates.Event | None:
        event_model = await self._try_get_one(
            model_class=self._model_class,
            id=event_id,
            load_configs={
                sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                    models.Game.teams,
                ),
            },
        )
        if event_model:
            return self._parse_event_model(event_model)

    async def get_events(self, limit: int, offset: int) -> list[aggregates.Event]:
        event_models = await self._get_many(
            model_class=self._model_class,
            where=(),
            order_by=(),
            limit=limit,
            offset=offset,
            load_configs={
                sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                    models.Game.teams,
                ),
            },
        )
        return [self._parse_event_model(event_model) for event_model in event_models]

    async def save_event(self, event: aggregates.Event) -> aggregates.Event:
        event_model = models.Event(
            id=event.id,
            start_dt=event.start_dt,
            title=event.title,
            type=event.type,
            description=event.description,
            price=event.price,
            image_urls=event.image_urls,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        return self._parse_event_model(
            await self._save(
                event_model,
                load_configs={
                    sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                        models.Game.teams,
                    ),
                },
            )
        )

    async def delete_event(self, event_id: types.EventId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=event_id,
                model_class=self._model_class,
            ),
        )
