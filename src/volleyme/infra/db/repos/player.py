from src.volleyme.domain import aggregates, repos, types
from src.volleyme.infra.db import models

from . import base


class PlayerRepo(
    base.SQLAlchemyIdModelRepo,
    repos.PlayerRepo,
):
    """Player repository implementation."""

    _model_class = models.Player

    def _parse_player_model(self, player_model: models.Player) -> aggregates.Player:
        return aggregates.Player(
            id=types.PlayerId(player_model.id),
            type=player_model.type,
            user_id=types.UserId(player_model.user_id),
            rating=player_model.rating,
            created_at=player_model.created_at,
            updated_at=player_model.updated_at,
        )

    async def get_player(self, player_id: types.PlayerId) -> aggregates.Player | None:
        player_model, _ = await self._try_get_one(
            model_class=self._model_class,
            id=(player_id,),
        )
        if player_model:
            return self._parse_player_model(player_model)
        return None

    async def get_players(self, limit: int, offset: int) -> list[aggregates.Player]:
        player_models, _ = await self._get_many(
            model_class=self._model_class,
            where=(),
            order_by=(),
            limit=limit,
            offset=offset,
        )
        return [
            self._parse_player_model(player_model) for player_model in player_models
        ]

    async def get_players_by_ids(
        self,
        player_ids: list[types.PlayerId],
    ) -> list[aggregates.Player]:
        if not player_ids:
            return []
        player_models, _ = await self._get_many(
            model_class=self._model_class,
            where=(self._model_class.id.in_(player_ids),),
            order_by=(),
        )
        return [
            self._parse_player_model(player_model) for player_model in player_models
        ]

    async def save_player(
        self,
        player: aggregates.Player,
        create: bool = False,
    ) -> aggregates.Player:
        player_model = models.Player(
            id=player.id,
            type=player.type,
            user_id=player.user_id,
            rating=player.rating,
        )
        return self._parse_player_model(await self._save(player_model, create=create))

    async def delete_player(self, player_id: types.PlayerId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=(player_id,),
                model_class=self._model_class,
            ),
        )
