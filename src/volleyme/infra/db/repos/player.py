from src.common import repos as common_repos
from src.volleyme.domain import aggregates, repos, types
from src.volleyme.infra.db import models


class PlayerRepo(
    common_repos.SQLAlchemyIdModelRepo,
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
        player_model = await self._try_get_one(
            model_class=self._model_class, id=player_id
        )
        if player_model:
            return self._parse_player_model(player_model)

    async def get_players(self, limit: int, offset: int) -> list[aggregates.Player]:
        return [
            self._parse_player_model(player_model)
            for player_model in await self._get_many(
                model_class=self._model_class,
                where=(),
                order_by=(),
                limit=limit,
                offset=offset,
            )
        ]

    async def get_players_by_ids(
        self,
        player_ids: list[types.PlayerId],
    ) -> list[aggregates.Player]:
        if not player_ids:
            return []
        return [
            self._parse_player_model(player_model)
            for player_model in await self._get_many(
                model_class=self._model_class,
                where=(self._model_class.id.in_(player_ids),),
                order_by=(),
            )
        ]

    async def save_player(self, player: aggregates.Player) -> aggregates.Player:
        player_model = models.Player(
            id=player.id,
            type=player.type,
            user_id=player.user_id,
            rating=player.rating,
        )
        return self._parse_player_model(await self._save(player_model))

    async def delete_player(self, player_id: types.PlayerId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=(player_id,),
                model_class=self._model_class,
            ),
        )
