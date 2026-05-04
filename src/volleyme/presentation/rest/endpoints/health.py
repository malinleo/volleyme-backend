import typing

import fastapi.responses
from dependency_injector import wiring

from src.volleyme import di
from src.volleyme.application import usecases
from src.volleyme.presentation.rest import schemas

health_router = fastapi.APIRouter(prefix="/healthz", tags=["health"])


@health_router.get("/", response_model=schemas.HealthCheckResponse)
@wiring.inject
async def health_check(
    usecase: typing.Annotated[
        usecases.HealthCheckUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.health_check]]),
    ],
):
    result = await usecase.execute()
    response_schema = schemas.HealthCheckResponse.model_validate(result)
    if not result.is_healthy:
        return fastapi.responses.JSONResponse(
            status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response_schema.model_dump(mode="json"),
        )
    return response_schema
