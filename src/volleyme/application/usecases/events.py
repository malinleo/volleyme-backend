import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.common import usecases
from src.volleyme.application import dto, query_repos, services
from src.volleyme.domain import aggregates, repos, types
from src.volleyme.domain import exc as domain_exc


@dataclasses.dataclass(frozen=True)
class GetEventByIdUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo
    event_query_repo: query_repos.EventQueryRepo
    event_invitation_repo: repos.EventInvitationRepo
    token_service: services.token.TokenService

    async def execute(
        self,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
        invitation_token: str | None = None,
    ) -> dto.EventDetailsDto:
        event = await self.event_repo.get_event(types.EventId(event_id))
        if not event:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")
        if not event.is_visible_for_user(types.UserId(user_id)):
            if not invitation_token:
                raise usecases.exc.NotFound(
                    message=f"Event with id {event_id} not found",
                )
            try:
                token_payload = self.token_service.decode(invitation_token)
            except services.exc.ApplicationServiceError as error:
                raise usecases.exc.UseCaseError.from_error(error) from error
            invitation = await self.event_invitation_repo.get_invitation(
                types.EventInvitationId(token_payload["sub"]),
            )
            if not invitation:
                raise usecases.exc.NotFound(message="Invalid invitation token")
            try:
                invitation.is_usable(
                    types.EventId(event_id),
                    types.UserId(user_id),
                    datetime.datetime.now(datetime.UTC),
                )
            except domain_exc.DomainError as error:
                raise usecases.exc.UseCaseError.from_error(error) from error
            await self.event_invitation_repo.save_invitation(invitation, create=False)
        event_info = await self.event_query_repo.get_event_info_for_user(
            types.EventId(event_id),
            types.UserId(user_id),
        )
        if not event_info:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")
        return event_info


@dataclasses.dataclass(frozen=True)
class GetEventsUseCase(usecases.BaseUseCase):
    event_query_repo: query_repos.EventQueryRepo

    async def execute(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
        only_my_events: bool = False,
        end_before: datetime.datetime | None = None,
        end_after: datetime.datetime | None = None,
    ) -> list[dto.EventListDto]:
        return await self.event_query_repo.get_events_info_for_user(
            types.UserId(user_id),
            limit,
            offset,
            only_my_events,
            end_before,
            end_after,
        )


@dataclasses.dataclass(frozen=True)
class CreateEventUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo
    event_query_repo: query_repos.EventQueryRepo

    async def execute(
        self,
        event: dto.CreateEventDto,
        creator_id: uuid.UUID,
    ) -> dto.EventDetailsDto:
        creator_user_id = types.UserId(creator_id)
        try:
            new_event = aggregates.Event.create(
                title=event.title,
                start_dt=event.start_dt,
                end_dt=event.end_dt,
                game_type=event.game_type,
                format_type=event.format_type,
                max_participants_count=event.max_participants_count,
                country=event.country,
                city=event.city,
                address=event.address,
                description=event.description,
                price=event.price,
                currency=event.currency,
                image_urls=event.image_urls,
                creator_user_id=creator_user_id,
                is_public=event.is_public,
            )
        except domain_exc.DomainError as domain_error:
            raise usecases.exc.UseCaseError.from_error(
                domain_error,
            ) from domain_error
        try:
            event_aggregate = await self.event_repo.save_event(new_event, create=True)
        except repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to create event"],
                    )
                ],
            ) from e
        event_info = await self.event_query_repo.get_event_info_for_user(
            event_aggregate.id,
            creator_user_id,
        )
        if not event_info:
            raise usecases.exc.NotFound(
                message=f"Event with id {event_aggregate.id} not found",
            )
        return event_info


@dataclasses.dataclass(frozen=True)
class DeleteEventUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo

    async def execute(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        event_aggregate = await self.event_repo.get_event(types.EventId(event_id))
        if not event_aggregate:
            raise usecases.exc.NotFound(
                message=f"Event with id {event_id} not found",
            )
        validators = [
            services.validators.CanDeleteEventValidator(
                user_id=types.UserId(user_id),
                event=event_aggregate,
            )
        ]
        self._run_validation(validators)
        try:
            await self.event_repo.delete_event(event_aggregate.id)
        except repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to delete event"],
                    )
                ],
            ) from e


@dataclasses.dataclass(frozen=True)
class JoinEventUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo
    event_invitation_repo: repos.EventInvitationRepo
    token_service: services.token.TokenService

    async def execute(
        self,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
        invitation_token: str | None = None,
    ) -> None:
        event = await self.event_repo.get_event(types.EventId(event_id))
        if not event:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")

        if not event.is_visible_for_user(types.UserId(user_id)):
            if not invitation_token:
                raise usecases.exc.NotFound(
                    message=f"Event with id {event_id} not found",
                )
            try:
                token_payload = self.token_service.decode(invitation_token)
            except services.exc.ApplicationServiceError as error:
                raise usecases.exc.UseCaseError.from_error(error) from error

            invitation = await self.event_invitation_repo.get_invitation(
                types.EventInvitationId(token_payload["sub"]),
            )
            if not invitation:
                raise usecases.exc.NotFound(message="Invalid invitation token")

            try:
                invitation.use(
                    types.EventId(event_id),
                    types.UserId(user_id),
                    datetime.datetime.now(datetime.UTC),
                )
            except domain_exc.DomainError as error:
                raise usecases.exc.UseCaseError.from_error(error) from error

            await self.event_invitation_repo.save_invitation(invitation, create=False)

        event.add_participant(types.UserId(user_id))
        await self.event_repo.save_event(event, create=False)


@dataclasses.dataclass(frozen=True)
class LeaveEventUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo

    async def execute(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        event_aggregate = await self.event_repo.get_event(types.EventId(event_id))
        if not event_aggregate:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")
        validators = [
            services.validators.CanLeaveEventValidator(
                user_id=types.UserId(user_id),
                event=event_aggregate,
            )
        ]
        self._run_validation(validators)
        event_aggregate.remove_participant(types.UserId(user_id))
        await self.event_repo.save_event(event_aggregate, create=False)


@dataclasses.dataclass(frozen=True)
class ChangePrivacyUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo
    event_query_repo: query_repos.EventQueryRepo

    async def execute(
        self,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
        is_public: bool,
    ) -> dto.EventDetailsDto:
        event_aggregate = await self.event_repo.get_event(types.EventId(event_id))
        if not event_aggregate:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")

        current_dt = datetime.datetime.now(datetime.UTC)
        if is_public:
            try:
                event_aggregate.make_public(types.UserId(user_id), current_dt)
            except domain_exc.DomainError as error:
                raise usecases.exc.UseCaseError.from_error(error) from error
        else:
            try:
                event_aggregate.make_private(types.UserId(user_id), current_dt)
            except domain_exc.DomainError as error:
                raise usecases.exc.UseCaseError.from_error(error) from error
        event_aggregate = await self.event_repo.save_event(
            event_aggregate,
            create=False,
        )
        event_info = await self.event_query_repo.get_event_info_for_user(
            event_aggregate.id,
            types.UserId(user_id),
        )
        if not event_info:
            raise usecases.exc.NotFound(
                message=f"Event with id {event_aggregate.id} not found",
            )
        return event_info
