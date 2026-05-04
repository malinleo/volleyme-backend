import typing

import fastapi
from dependency_injector import wiring

from src.volleyme import di
from src.volleyme.application import services as app_services
from src.volleyme.application import usecases
from src.volleyme.infra import services
from src.volleyme.presentation.rest.v0_1_0 import deps, schemas

auth_router = fastapi.APIRouter(prefix="/auth")


@auth_router.post("/login/", response_model=schemas.JWTAuthTokenResponse)
@wiring.inject
async def login(
    credentials: schemas.LoginRequest,
    container: typing.Annotated[
        di.DI,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.container]]),
    ],
    generate_auth_token_strategy: typing.Annotated[
        app_services.auth.GenerateAuthTokenStrategy,
        fastapi.Depends(
            wiring.Closing[wiring.Provide[di.DI.infra.generate_auth_token_strategy]]
        ),
    ],
):
    credentials_dto = services.UsernamePasswordCredentials(
        username=credentials.username,
        password=credentials.password,
    )
    login_usecase: usecases.LoginUseCase = await container.usecases.login(
        login_strategy__credentials=credentials_dto,
    )
    auth_token_pair = await generate_auth_token_strategy.generate(
        user=await login_usecase.execute(),
    )
    return schemas.JWTAuthTokenResponse(
        token_type=auth_token_pair.schema,
        access_token=auth_token_pair.access_token,
        refresh_token=auth_token_pair.refresh_token,
    )


@auth_router.post("/register/", response_model=schemas.JWTAuthTokenResponse)
@wiring.inject
async def register(
    user_data: schemas.RegisterRequest,
    register_usecase: typing.Annotated[
        usecases.RegisterUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.register]]),
    ],
    generate_auth_token_strategy: typing.Annotated[
        app_services.auth.GenerateAuthTokenStrategy,
        fastapi.Depends(
            wiring.Closing[wiring.Provide[di.DI.infra.generate_auth_token_strategy]]
        ),
    ],
):
    auth_token_pair = await generate_auth_token_strategy.generate(
        user=await register_usecase.execute(
            username=user_data.username,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=user_data.avatar_url,
        ),
    )
    return schemas.JWTAuthTokenResponse(
        token_type=auth_token_pair.schema,
        access_token=auth_token_pair.access_token,
        refresh_token=auth_token_pair.refresh_token,
    )


@auth_router.post("/logout/", response_model=schemas.JWTAuthTokenResponse)
@wiring.inject
async def logout(
    user: deps.AuthUserDependencyType,
    logout_usecase: typing.Annotated[
        usecases.LogoutUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.logout]]),
    ],
):
    await logout_usecase.execute(user=user)
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)


@auth_router.post("/refresh/", response_model=schemas.JWTAuthTokenResponse)
@wiring.inject
async def refresh(
    refresh_token: str,
    refresh_usecase: typing.Annotated[
        usecases.RefreshTokenUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.refresh]]),
    ],
    generate_auth_token_strategy: typing.Annotated[
        app_services.auth.GenerateAuthTokenStrategy,
        fastapi.Depends(
            wiring.Closing[wiring.Provide[di.DI.infra.generate_auth_token_strategy]]
        ),
    ],
):
    auth_token_pair = await generate_auth_token_strategy.generate(
        user=await refresh_usecase.execute(refresh_token=refresh_token),
    )
    return schemas.JWTAuthTokenResponse(
        token_type=auth_token_pair.schema,
        access_token=auth_token_pair.access_token,
        refresh_token=auth_token_pair.refresh_token,
    )
