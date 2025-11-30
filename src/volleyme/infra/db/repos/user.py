from src.volleyme.domain import repos, types, aggregates
from src.common import repos as common_repos
from src.volleyme.infra.db import models
import sqlalchemy.orm


class UserRepo(
    common_repos.SQLAlchemyIdModelRepo,
    repos.UserRepo,
):
    """User repository implementation."""

    _model_class = models.User

    def _parse_user_model(self, user_model: models.User) -> aggregates.User:
        user = aggregates.User(
            id=types.UserId(user_model.id),
            email=user_model.email,
            password=user_model.password,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
        )
        if user_model.profile:
            user.profile = aggregates.Profile(
                user=user,
                created_at=user_model.profile.created_at,
                updated_at=user_model.profile.updated_at,
                first_name=user_model.profile.first_name,
                last_name=user_model.profile.last_name,
                avatar_url=user_model.profile.avatar_url,
            )
        return user

    async def get_user(self, user_id: types.UserId) -> aggregates.User | None:
        user_model = await self._try_get_one(model_class=self._model_class, id=user_id)
        if user_model:
            return self._parse_user_model(user_model)

    async def get_users(self, limit: int, offset: int) -> list[aggregates.User]:
        return [
            self._parse_user_model(user_model)
            for user_model in await self._get_many(
                model_class=self._model_class,
                where=(),
                order_by=(),
                limit=limit,
                offset=offset,
            )
        ]

    async def save_user(self, user: aggregates.User) -> aggregates.User:
        user_model = models.User(
            id=user.id,
            email=user.email,
            password=user.password,
        )
        if user.profile:
            user_model.profile = models.Profile(
                user_id=user.id,
                first_name=user.profile.first_name,
                last_name=user.profile.last_name,
                avatar_url=user.profile.avatar_url,
            )
        user_model = await self._save(
            user_model,
            load_configs={sqlalchemy.orm.joinedload(self._model_class.profile)},
        )
        return self._parse_user_model(user_model)

    async def delete_user(self, user_id: types.UserId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=user_id,
                model_class=self._model_class,
            ),
        )
