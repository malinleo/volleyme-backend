from src.volleyme.domain import aggregates, repos, types
from src.volleyme.infra.db import models

from . import base


class UserSessionRepo(
    base.SQLAlchemyIdModelRepo,
    repos.UserSessionRepo,
):
    """User session repository implementation."""

    _model_class = models.UserSession

    def _parse_model(self, model: models.UserSession) -> aggregates.UserSession:
        return aggregates.UserSession(
            id=types.UserSessionId(model.id),
            user_id=types.UserId(model.user_id),
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_session(
        self,
        session_id: types.UserSessionId,
    ) -> aggregates.UserSession | None:
        model, _ = await self._try_get_one(
            id=(session_id,),
            model_class=self._model_class,
        )
        if model:
            return self._parse_model(model)
        return None

    async def get_user_sessions(
        self,
        user_id: types.UserId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[aggregates.UserSession]:
        session_models, _ = await self._get_many(
            model_class=self._model_class,
            where=(self._model_class.user_id == user_id,),
            limit=limit,
            offset=offset,
        )
        return [self._parse_model(model) for model in session_models]

    async def save_session(
        self,
        session: aggregates.UserSession,
        create: bool = False,
    ) -> aggregates.UserSession:
        model = models.UserSession(
            id=session.id,
            user_id=session.user_id,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
        )
        model = await self._save(model, create=create)
        return self._parse_model(model)

    async def delete_session(self, session_id: types.UserSessionId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=(session_id,),
                model_class=self._model_class,
            ),
        )
