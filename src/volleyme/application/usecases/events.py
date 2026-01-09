import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.common import repos as common_repos
from src.common import usecases
from src.volleyme.application import dto, query_repos
from src.volleyme.domain import aggregates, repos, types


@dataclasses.dataclass(frozen=True)
class GetEventByIdUseCase:
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
        raise usecases.exc.NotFound(
            details=[
                common_exc.ErrorDetail(message=f"Event with id {event_id} not found"),
            ],
        )


@dataclasses.dataclass(frozen=True)
class GetEventsUseCase:
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
class CreateEventUseCase:
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
                    participants=[creator_user_id],
                    hosts=[creator_user_id],
                    created_by=creator_user_id,
                    updated_by=creator_user_id,
                ),
                create=True,
            )
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Failed to create event, reason: {e}"
                    ),
                ],
            ) from e
        event_info = await self.event_query_repo.get_event_info_for_user(
            event_aggregate.id,
            creator_user_id,
        )
        if not event_info:
            raise usecases.exc.NotFound(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Event with id {event_aggregate.id} not found",
                    ),
                ],
            )
        return event_info


@dataclasses.dataclass(frozen=True)
class UpdateEventUseCase:
    event_repo: repos.EventRepo
    event_query_repo: query_repos.EventQueryRepo

    async def execute(
        self,
        event_id: uuid.UUID,
        event: dto.UpdateEventDto,
        updater_id: uuid.UUID,
    ) -> dto.EventDetailsDto:
        try:
            event_aggregate = await self.event_repo.get_event(
                types.EventId(event_id),
            )
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(message=f"Failed to get event, reason: {e}"),
                ],
            ) from e
        if not event_aggregate:
            raise usecases.exc.NotFound(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Event with id {event_id} not found",
                    ),
                ],
            )
        updater_user_id = types.UserId(updater_id)
        if event_aggregate.created_by != updater_user_id:
            raise usecases.exc.PermissionDenied(
                details=[
                    common_exc.ErrorDetail(
                        message="You are not allowed to update this event"
                    ),
                ],
            )
        event_aggregate.title = event.title
        event_aggregate.start_dt = event.start_dt.astimezone(datetime.UTC)
        event_aggregate.end_dt = event.end_dt.astimezone(datetime.UTC)
        event_aggregate.country = event.country
        event_aggregate.city = event.city
        event_aggregate.address = event.address
        event_aggregate.description = event.description
        event_aggregate.price = event.price
        event_aggregate.currency = event.currency
        event_aggregate.image_urls = event.image_urls
        event_aggregate.updated_by = updater_user_id
        try:
            event_aggregate = await self.event_repo.save_event(
                event_aggregate,
                create=False,
            )
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Failed to create event, reason: {e}"
                    ),
                ],
            ) from e
        event_info = await self.event_query_repo.get_event_info_for_user(
            event_aggregate.id,
            updater_user_id,
        )
        if not event_info:
            raise usecases.exc.NotFound(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Event with id {event_aggregate.id} not found",
                    ),
                ],
            )
        return event_info


@dataclasses.dataclass(frozen=True)
class DeleteEventUseCase:
    event_repo: repos.EventRepo

    async def execute(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        event_aggregate = await self.event_repo.get_event(types.EventId(event_id))
        if not event_aggregate:
            raise usecases.exc.NotFound(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Event with id {event_id} not found"
                    ),
                ],
            )
        if event_aggregate.created_by != types.UserId(user_id):
            raise usecases.exc.PermissionDenied(
                details=[
                    common_exc.ErrorDetail(
                        message="You are not allowed to delete this event"
                    ),
                ],
            )
        try:
            await self.event_repo.delete_event(event_aggregate.id)
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        message=f"Failed to delete event, reason: {e}"
                    ),
                ],
            ) from e
