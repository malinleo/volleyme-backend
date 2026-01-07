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
async def email_password_login(
    credentials: schemas.EmailPasswordLoginRequest,
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
    credentials_dto = services.EmailPasswordCredentials(
        email=credentials.email,
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
async def email_password_register(
    credentials: schemas.EmailPasswordRegisterRequest,
    register_usecase: typing.Annotated[
        usecases.EmailPasswordRegisterUseCase,
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
        await register_usecase.execute(credentials.email, credentials.password)
    )
    return schemas.JWTAuthTokenResponse(
        token_type=auth_token.schema,
        access_token=auth_token.token,
    )
