import typing

import fastapi
from dependency_injector import wiring

from src.volleyme.application import usecases
from src.volleyme.infra import di, services
from src.volleyme.presentation import auth
from src.volleyme.presentation.rest import schemas

auth_router = fastapi.APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login/", response_model=schemas.JWTAuthTokenResponse)
@wiring.inject
async def login(
    credentials: schemas.LoginRequest,
    container: typing.Annotated[
        di.DI,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.container]]),
    ],
    generate_auth_token_strategy: typing.Annotated[
        auth.GenerateAuthTokenStrategy,
        fastapi.Depends(
            wiring.Closing[wiring.Provide[di.DI.infra.generate_auth_token_strategy]]
        ),
    ],
):
    credentials_dto = services.UsernamePasswordCredentials(
        username=credentials.username,
        password=credentials.password,
    )
    login_usecase: usecases.AuthUseCase = await container.usecases.login(
        auth_strategy__credentials=credentials_dto,
    )
    auth_token = await generate_auth_token_strategy.generate(
        await login_usecase.execute()
    )
    return schemas.JWTAuthTokenResponse(
        token_type=auth_token.schema,
        access_token=auth_token.token,
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
        auth.GenerateAuthTokenStrategy,
        fastapi.Depends(
            wiring.Closing[wiring.Provide[di.DI.infra.generate_auth_token_strategy]]
        ),
    ],
):
    auth_token = await generate_auth_token_strategy.generate(
        await register_usecase.execute(
            username=user_data.username,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=user_data.avatar_url,
        )
    )
    return schemas.JWTAuthTokenResponse(
        token_type=auth_token.schema,
        access_token=auth_token.token,
    )
