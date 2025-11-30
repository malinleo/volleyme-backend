import dataclasses
import uuid
import datetime
from src.volleyme.domain import repos, aggregates, types
from src.common import usecases, repos as common_repos
from src.volleyme.application import dto


@dataclasses.dataclass(frozen=True)
class GetEventByIdUseCase:
    event_repo: repos.EventRepo

    async def execute(self, event_id: uuid.UUID) -> aggregates.Event:
        if event := await self.event_repo.get_event(types.EventId(event_id)):
            return event
        raise usecases.exc.NotFound(msg=f"Event with id {event_id} not found")


@dataclasses.dataclass(frozen=True)
class GetEventsUseCase:
    event_repo: repos.EventRepo

    async def execute(self, limit: int, offset: int) -> list[aggregates.Event]:
        return await self.event_repo.get_events(limit, offset)


@dataclasses.dataclass(frozen=True)
class CreateEventUseCase:
    event_repo: repos.EventRepo

    async def execute(self, event: dto.CreateEventDto) -> aggregates.Event:
        try:
            return await self.event_repo.save_event(
                aggregates.Event(
                    start_dt=event.start_dt.astimezone(datetime.UTC),
                    title=event.title,
                    type=event.type,
                    description=event.description,
                    price=event.price,
                    image_urls=event.image_urls,
                    games=[],
                )
            )
        except common_repos.exc.RepoError as e:
            raise usecases.exc.UseCaseError(
                msg="Failed to create event, reason: " + str(e)
            ) from e
