import datetime
import typing
import uuid

import fastapi
from dependency_injector import wiring

from src.volleyme import di
from src.volleyme.application import dto, usecases
from src.volleyme.presentation.rest.v0_1_0 import deps, schemas

events_router = fastapi.APIRouter(
    prefix="/events",
    dependencies=[fastapi.Depends(deps.authenticate_user)],
)


@events_router.get("/{event_id}/", response_model=schemas.EventDetailResponse)
@wiring.inject
async def get_event(
    usecase: typing.Annotated[
        usecases.GetEventByIdUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.get_event_by_id]]),
    ],
    event_id: uuid.UUID,
    user: deps.AuthUserDependencyType,
    invitation_token: str = fastapi.Query(default=None),
):
    return schemas.EventDetailResponse.model_validate(
        await usecase.execute(event_id, user.id, invitation_token),
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
    pagination_params: typing.Annotated[
        schemas.PaginationParams,
        fastapi.Depends(deps.get_pagination_params),
    ],
    only_my_events: bool = fastapi.Query(default=False),
    end_before: datetime.datetime = fastapi.Query(default=None),
    end_after: datetime.datetime = fastapi.Query(default=None),
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
                only_my_events,
                end_before,
                end_after,
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


@events_router.post(
    "/{event_id}/change-privacy/",
    response_model=schemas.EventDetailResponse,
)
@wiring.inject
async def change_privacy(
    usecase: typing.Annotated[
        usecases.ChangePrivacyUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.change_privacy]]),
    ],
    event_id: uuid.UUID,
    change_privacy_data: schemas.ChangePrivacyRequest,
    user: deps.AuthUserDependencyType,
):
    return schemas.EventDetailResponse.model_validate(
        await usecase.execute(event_id, user.id, change_privacy_data.is_public),
    )


@events_router.delete("/{event_id}/")
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


@events_router.post("/{event_id}/join/")
@wiring.inject
async def join_event(
    usecase: typing.Annotated[
        usecases.JoinEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.join_event]]),
    ],
    event_id: uuid.UUID,
    user: deps.AuthUserDependencyType,
):
    await usecase.execute(event_id, user.id)
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)


@events_router.post("/{event_id}/leave/")
@wiring.inject
async def leave_event(
    usecase: typing.Annotated[
        usecases.LeaveEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.leave_event]]),
    ],
    event_id: uuid.UUID,
    user: deps.AuthUserDependencyType,
):
    await usecase.execute(event_id, user.id)
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)
