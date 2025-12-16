import dataclasses
import datetime
import uuid

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
        raise usecases.exc.NotFound(msg=f"Event with id {event_id} not found")


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
        creator_id: types.UserId,
    ) -> dto.EventDetailsDto:
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
                    participants=[creator_id],
                    hosts=[creator_id],
                    created_by=creator_id,
                    updated_by=creator_id,
                )
            )
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                msg="Failed to create event, reason: " + str(e)
            ) from e
        event_info = await self.event_query_repo.get_event_info_for_user(
            types.EventId(event_aggregate.id),
            types.UserId(creator_id),
        )
        if not event_info:
            raise usecases.exc.NotFound(
                msg=f"Event with id {event_aggregate.id} not found"
            )
        return event_info
