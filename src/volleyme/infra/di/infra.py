import string

import sqlalchemy.ext.asyncio
from dependency_injector import containers, providers

from src.common import models as common_models
from src.config import settings
from src.volleyme.infra import services
from src.volleyme.infra.db import repos


class Infra(containers.DeclarativeContainer):
    async_engine = providers.Singleton(
        sqlalchemy.ext.asyncio.create_async_engine,
        url=settings.db_url,
        echo=settings.DEBUG,
    )
    async_session_factory = providers.Resource(
        sqlalchemy.ext.asyncio.async_sessionmaker,
        async_engine,
        expire_on_commit=False,
    )
    db_session = providers.Resource(
        common_models.get_db_session,
        async_session_factory=async_session_factory,
    )
    jwt_codec = providers.Factory(
        services.JWTCodecService,
        public_key=settings.jwt_public_key,
        private_key=settings.jwt_private_key,
        algorithm=settings.JWT_ALGORITHM,
    )
    auth_strategy = providers.Factory(
        services.JWTAuthStrategy,
        token_service=jwt_codec,
    )
    user_query_repo = providers.Factory(repos.UserQueryRepo, db_session=db_session)
    login_auth_strategy = providers.Factory(
        services.EmailPasswordAuthStrategy,
        user_query_repo=user_query_repo,
    )
    generate_auth_token_strategy = providers.Factory(
        services.JWTAuthTokenStrategy,
        token_service=jwt_codec,
        expires_in=settings.JWT_EXPIRES_IN,
    )
    event_repo = providers.Factory(repos.EventRepo, db_session=db_session)
    event_query_repo = providers.Factory(repos.EventQueryRepo, db_session=db_session)
    player_repo = providers.Factory(repos.PlayerRepo, db_session=db_session)
    user_repo = providers.Factory(repos.UserRepo, db_session=db_session)
    password_validator = providers.Factory(
        services.password.PasswordValidator,
        policies=[
            services.password.MinLength(min_length=settings.PASSWORD_MIN_LENGTH),
            services.password.MaxLength(max_length=settings.PASSWORD_MAX_LENGTH),
            services.password.ContainsChars(
                chars=set(string.ascii_uppercase),
                chars_type_name="uppercase letter",
                error_code="no_uppercase",
            ),
            services.password.ContainsChars(
                chars=set(string.ascii_lowercase),
                chars_type_name="lowercase letter",
                error_code="no_lowercase",
            ),
            services.password.ContainsChars(
                chars=set(string.digits),
                chars_type_name="digit",
                error_code="no_digit",
            ),
            services.password.ContainsChars(
                chars=set(string.punctuation),
                chars_type_name="special character",
                error_code="no_special",
            ),
        ],
    )
