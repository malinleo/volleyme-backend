import dataclasses
import datetime
import uuid

from src.common import usecases
from src.config import settings
from src.volleyme.application import dto, services
from src.volleyme.domain import aggregates, repos, types

from . import exc


@dataclasses.dataclass(frozen=True)
class InviteToEventUseCaseDeps:
    event_repo: repos.EventRepo
    event_invitation_repo: repos.EventInvitationRepo


@dataclasses.dataclass(frozen=True)
class InviteToEventUseCase(usecases.BaseUseCase):
    uow: services.uow.UOW[InviteToEventUseCaseDeps]
    token_service: services.token.TokenService

    @exc.wrap_errors
    async def execute(
        self,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
        invited_user_id: uuid.UUID | None = None,
    ) -> dto.InvitationDetailDto:
        event = await self.uow.d.event_repo.get_event(types.EventId(event_id))
        if not event:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")
        if not event.is_user_host(types.UserId(user_id)):
            raise usecases.exc.PermissionDenied(
                message="You are not a host of the event",
            )
        invitation_id = types.EventInvitationId(uuid.uuid4())
        new_invitation = aggregates.EventInvitation.create(
            id=invitation_id,
            event_id=types.EventId(event_id),
            user_id=types.UserId(invited_user_id) if invited_user_id else None,
            token=self.token_service.encode({"sub": str(invitation_id)}),
            expires_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=settings.EVENT_INVITATION_EXPIRATION_SECONDS),
        )
        invitation = await self.uow.d.event_invitation_repo.save_invitation(
            new_invitation,
            create=True,
        )
        return dto.InvitationDetailDto(
            id=invitation.id,
            event_id=invitation.event_id,
            user_id=invitation.user_id,
            token=invitation.token,
            expires_at=invitation.expires_at,
            used_at=invitation.used_at,
        )
