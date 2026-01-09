import typing
import uuid

import fastapi
from dependency_injector import wiring

from src.volleyme.application import dto, usecases
from src.volleyme.infra import di
from src.volleyme.presentation.rest import deps, schemas

events_router = fastapi.APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[fastapi.Depends(deps.authenticate_user)],
)


@events_router.get("/{event_id}", response_model=schemas.EventDetailResponse)
@wiring.inject
async def get_event(
    usecase: typing.Annotated[
        usecases.GetEventByIdUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.get_event_by_id]]),
    ],
    event_id: uuid.UUID,
    user: deps.AuthUserDependencyType,
):
    return schemas.EventDetailResponse.model_validate(
        await usecase.execute(event_id, user.id),
    )


@events_router.get(
    "/",
    response_model=schemas.PaginatedResponse[schemas.EventListResponse],
)
@wiring.inject
async def get_events(
    request: fastapi.Request,
    usecase: typing.Annotated[
        usecases.GetEventsUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.get_events]]),
    ],
    user: deps.AuthUserDependencyType,
    pagination_params: schemas.PaginationParams = fastapi.Depends(
        deps.get_pagination_params,
    ),
):
    return schemas.PaginatedResponse.build(
        request,
        pagination_params,
        items=[
            schemas.EventListResponse.model_validate(event)
            for event in await usecase.execute(
                user.id,
                pagination_params.limit,
                pagination_params.offset,
            )
        ],
    )


@events_router.post("/", response_model=schemas.EventDetailResponse)
@wiring.inject
async def create_event(
    usecase: typing.Annotated[
        usecases.CreateEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.create_event]]),
    ],
    event: schemas.CreateEventRequest,
    user: deps.AuthUserDependencyType,
):
    return schemas.EventDetailResponse.model_validate(
        await usecase.execute(dto.CreateEventDto.model_validate(event), user.id),
    )


@events_router.put("/{event_id}", response_model=schemas.EventDetailResponse)
@wiring.inject
async def update_event(
    usecase: typing.Annotated[
        usecases.UpdateEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.update_event]]),
    ],
    event_id: uuid.UUID,
    event: schemas.UpdateEventRequest,
    user: deps.AuthUserDependencyType,
):
    return schemas.EventDetailResponse.model_validate(
        await usecase.execute(
            event_id,
            dto.UpdateEventDto.model_validate(event),
            user.id,
        ),
    )


@events_router.delete("/{event_id}")
@wiring.inject
async def delete_event(
    usecase: typing.Annotated[
        usecases.DeleteEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.delete_event]]),
    ],
    event_id: uuid.UUID,
    user: deps.AuthUserDependencyType,
):
    await usecase.execute(event_id, user.id)
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)
