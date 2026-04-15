import typing

import fastapi.params
import fastapi.security
from dependency_injector import wiring

from src.config import settings
from src.volleyme import di
from src.volleyme.application import services as app_services
from src.volleyme.application import usecases
from src.volleyme.infra import services

from . import auth, schemas


@wiring.inject
async def authenticate_user(
    container: typing.Annotated[
        di.DI,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.container]]),
    ],
    credentials: typing.Annotated[
        fastapi.security.HTTPAuthorizationCredentials,
        fastapi.Depends(auth.auth),
    ],
) -> app_services.auth.AuthUser:
    auth_usecase: usecases.AuthUseCase = await container.usecases.authenticate(
        auth_strategy__credentials=services.JWTCredentials(
            token=credentials.credentials,
        ),
    )
    return await auth_usecase.execute()


async def get_pagination_params(
    limit: int = fastapi.Query(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
    ),
    offset: int = fastapi.Query(default=0, ge=0),
) -> schemas.PaginationParams:
    return schemas.PaginationParams(limit=limit, offset=offset)


AuthUserDependency: fastapi.params.Depends = fastapi.Depends(
    authenticate_user,
)
AuthUserDependencyType: typing.TypeAlias = typing.Annotated[
    app_services.auth.AuthUser,
    AuthUserDependency,
]
