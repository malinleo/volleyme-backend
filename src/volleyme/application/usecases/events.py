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

    async def execute(self, event_id: uuid.UUID) -> dto.EventDetailsDto:
        if event_info := await self.event_query_repo.get_event_info(
            types.EventId(event_id),
        ):
            return event_info
        raise usecases.exc.NotFound(msg=f"Event with id {event_id} not found")


@dataclasses.dataclass(frozen=True)
class GetEventsUseCase:
    event_query_repo: query_repos.EventQueryRepo

    async def execute(self, limit: int, offset: int) -> list[dto.EventListDto]:
        return await self.event_query_repo.get_events_info(limit, offset)


@dataclasses.dataclass(frozen=True)
class CreateEventUseCase:
    event_repo: repos.EventRepo

    async def execute(self, event: dto.CreateEventDto) -> aggregates.Event:
        try:
            return await self.event_repo.save_event(
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
                    participants=[],
                    hosts=[],
                )
            )
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                msg="Failed to create event, reason: " + str(e)
            ) from e
