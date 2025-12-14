import typing
import uuid

import fastapi
from dependency_injector import wiring

from src.volleyme.application import dto, usecases
from src.volleyme.infra import di
from src.volleyme.presentation.rest import schemas

events_router = fastapi.APIRouter(prefix="/events", tags=["events"])


@events_router.get("/{event_id}", response_model=schemas.EventDetailResponse)
@wiring.inject
async def get_event(
    usecase: typing.Annotated[
        usecases.GetEventByIdUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.get_event_by_id]]),
    ],
    event_id: uuid.UUID,
):
    return schemas.EventDetailResponse.model_validate(await usecase.execute(event_id))


@events_router.get("/", response_model=list[schemas.EventListResponse])
@wiring.inject
async def get_events(
    usecase: typing.Annotated[
        usecases.GetEventsUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.get_events]]),
    ],
    user_id: uuid.UUID,
    limit: int = fastapi.Query(default=25, ge=1, le=100),
    offset: int = fastapi.Query(default=0, ge=0),
):
    return [
        schemas.EventListResponse.model_validate(event)
        for event in await usecase.execute(user_id, limit, offset)
    ]


@events_router.post("/")
@wiring.inject
async def create_event(
    usecase: typing.Annotated[
        usecases.CreateEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.create_event]]),
    ],
    event: schemas.CreateEventRequest,
):
    return schemas.EventDetailResponse.model_validate(
        await usecase.execute(dto.CreateEventDto.model_validate(event))
    )
