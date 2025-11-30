import fastapi
import typing
from dependency_injector import wiring
from src.volleyme.application import usecases, dto
from src.volleyme.infra import di
from src.volleyme.presentation.rest import schemas
import uuid

router = fastapi.APIRouter(prefix="/events", tags=["events"])


@router.get("/{event_id}", response_model=schemas.GetEventResponse)
@wiring.inject
async def get_event(
    usecase: typing.Annotated[
        usecases.GetEventByIdUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.get_event_by_id]]),
    ],
    event_id: uuid.UUID,
):
    return schemas.GetEventResponse.model_validate(await usecase.execute(event_id))


@router.post("/")
@wiring.inject
async def create_event(
    usecase: typing.Annotated[
        usecases.CreateEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.create_event]]),
    ],
    event: schemas.CreateEventRequest,
):
    return schemas.GetEventResponse.model_validate(
        await usecase.execute(dto.CreateEventDto.model_validate(event))
    )
