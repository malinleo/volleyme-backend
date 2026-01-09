import sqlalchemy.exc
import sqlalchemy.orm

from src.common import exc as common_exc
from src.common import repos as common_repos
from src.volleyme.application import dto, query_repos
from src.volleyme.domain import aggregates, repos, types
from src.volleyme.infra.db import models


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
            password_hash=aggregates.PasswordHash(value=user_model.password),
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
        user_model = await self._try_get_one(
            id=user_id,
            model_class=self._model_class,
            load_configs={sqlalchemy.orm.joinedload(self._model_class.profile)},
        )
        if user_model:
            return self._parse_user_model(user_model)
        return None

    async def get_users(self, limit: int, offset: int) -> list[aggregates.User]:
        return [
            self._parse_user_model(user_model)
            for user_model in await self._get_many(
                model_class=self._model_class,
                where=(),
                order_by=(),
                limit=limit,
                offset=offset,
                load_configs={sqlalchemy.orm.joinedload(self._model_class.profile)},
            )
        ]

    async def get_users_by_ids(
        self,
        user_ids: list[types.UserId],
    ) -> list[aggregates.User]:
        if not user_ids:
            return []
        return [
            self._parse_user_model(user_model)
            for user_model in await self._get_many(
                model_class=self._model_class,
                where=(self._model_class.id.in_(user_ids),),
                order_by=(),
                load_configs={sqlalchemy.orm.joinedload(self._model_class.profile)},
            )
        ]

    async def save_user(
        self,
        user: aggregates.User,
        create: bool = False,
    ) -> aggregates.User:
        user_model = models.User(
            id=user.id,
            email=user.email,
            password=user.password_hash.value,
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
            create=create,
            load_configs={sqlalchemy.orm.joinedload(self._model_class.profile)},
        )
        return self._parse_user_model(user_model)

    async def delete_user(self, user_id: types.UserId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=(user_id,),
                model_class=self._model_class,
            ),
        )


class UserQueryRepo(
    common_repos.SQLAlchemyIdModelRepo,
    query_repos.UserQueryRepo,
):
    """User query repository implementation."""

    _model_class = models.User

    async def get_user_auth_info(self, email: str) -> dto.UserAuthDto | None:
        query = sqlalchemy.select(self._model_class).where(
            self._model_class.email == email,
        )
        try:
            result = await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise common_repos.exc.QueryError(
                details=[common_exc.ErrorDetail(message=str(error))],
            ) from error
        user_model = result.unique().scalar_one_or_none()
        if user_model:
            return dto.UserAuthDto(
                id=types.UserId(user_model.id),
                email=user_model.email,
                password=user_model.password,
            )
        return None
