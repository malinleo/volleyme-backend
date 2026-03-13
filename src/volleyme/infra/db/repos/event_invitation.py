import datetime

from src.volleyme.domain import aggregates, repos, types
from src.volleyme.infra.db import models

from . import base


class EventInvitationRepo(
    base.SQLAlchemyIdModelRepo,
    repos.EventInvitationRepo,
):
    """Event invitation repository implementation."""

    _model_class = models.EventInvitation

    def _parse_invitation_model(
        self,
        invitation_model: models.EventInvitation,
    ) -> aggregates.EventInvitation:
        return aggregates.EventInvitation(
            id=types.EventInvitationId(invitation_model.id),
            event_id=types.EventId(invitation_model.event_id),
            user_id=types.UserId(invitation_model.user_id)
            if invitation_model.user_id
            else None,
            token=invitation_model.token,
            expires_at=invitation_model.expires_at.astimezone(datetime.UTC)
            if invitation_model.expires_at
            else None,
            used_at=invitation_model.used_at.astimezone(datetime.UTC)
            if invitation_model.used_at
            else None,
            created_at=invitation_model.created_at.astimezone(datetime.UTC),
            updated_at=invitation_model.updated_at.astimezone(datetime.UTC),
        )

    async def get_invitation(
        self,
        invitation_id: types.EventInvitationId,
    ) -> aggregates.EventInvitation | None:
        invitation_model, _ = await self._try_get_one(
            model_class=self._model_class,
            id=(invitation_id,),
        )
        if invitation_model:
            return self._parse_invitation_model(invitation_model)
        return None

    async def get_events(
        self,
        limit: int,
        offset: int,
    ) -> list[aggregates.EventInvitation]:
        invitation_models, _ = await self._get_many(
            model_class=self._model_class,
            where=(),
            order_by=(),
            limit=limit,
            offset=offset,
        )
        return [
            self._parse_invitation_model(invitation_model)
            for invitation_model in invitation_models
        ]

    async def save_invitation(
        self,
        invitation: aggregates.EventInvitation,
        create: bool = False,
    ) -> aggregates.EventInvitation:
        invitation_model = models.EventInvitation(
            id=invitation.id,
            event_id=invitation.event_id,
            user_id=invitation.user_id,
            token=invitation.token,
            expires_at=invitation.expires_at,
            used_at=invitation.used_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
        saved_invitation_model = await self._save(invitation_model, create=create)
        return self._parse_invitation_model(saved_invitation_model)

    async def delete_invitation(self, invitation_id: types.EventInvitationId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=(invitation_id,),
                model_class=self._model_class,
            ),
        )
