import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.common import usecases
from src.volleyme.application import dto, query_repos, services
from src.volleyme.domain import aggregates, repos, types


@dataclasses.dataclass(frozen=True)
class GetEventByIdUseCase(usecases.BaseUseCase):
    event_query_repo: query_repos.EventQueryRepo

    async def execute(
        self,
        event_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dto.EventDetailsDto:
        if event_info := await self.event_query_repo.get_event_info_for_user(
            types.EventId(event_id),
            types.UserId(user_id),
        ):
            return event_info
        raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")


@dataclasses.dataclass(frozen=True)
class GetEventsUseCase(usecases.BaseUseCase):
    event_query_repo: query_repos.EventQueryRepo

    async def execute(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> list[dto.EventListDto]:
        return await self.event_query_repo.get_events_info_for_user(
            types.UserId(user_id),
            limit,
            offset,
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
            event_aggregate = await self.event_repo.save_event(
                aggregates.Event(
                    title=event.title,
                    start_dt=event.start_dt.astimezone(datetime.UTC),
                    end_dt=event.end_dt.astimezone(datetime.UTC),
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
                    games=[],
                    participants={creator_user_id},
                    hosts={creator_user_id},
                    created_by=creator_user_id,
                    updated_by=creator_user_id,
                ),
                create=True,
            )
        except repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                detail=common_exc.ErrorDetail(
                    code=usecases.exc.UseCaseErrorCode.DEFAULT,
                    messages=["Failed to create event"],
                ),
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
                detail=common_exc.ErrorDetail(
                    code=usecases.exc.UseCaseErrorCode.DEFAULT,
                    messages=["Failed to delete event"],
                ),
            ) from e


@dataclasses.dataclass(frozen=True)
class JoinEventUseCase(usecases.BaseUseCase):
    event_repo: repos.EventRepo

    async def execute(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        event_aggregate = await self.event_repo.get_event(types.EventId(event_id))
        if not event_aggregate:
            raise usecases.exc.NotFound(message=f"Event with id {event_id} not found")
        validators = [
            services.validators.CanJoinEventValidator(
                user_id=types.UserId(user_id),
                event=event_aggregate,
            )
        ]
        self._run_validation(validators)
        event_aggregate.add_participant(types.UserId(user_id))
        await self.event_repo.save_event(event_aggregate, create=False)


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
