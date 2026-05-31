import string

import sqlalchemy.ext.asyncio
from dependency_injector import containers, providers

from src.common import models as common_models
from src.config import settings
from src.volleyme.application import usecases
from src.volleyme.infra import services
from src.volleyme.infra.db import repos


class Infra(containers.DeclarativeContainer):
    async_engine = providers.Singleton(
        sqlalchemy.ext.asyncio.create_async_engine,
        url=settings.db_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    async_session_factory = providers.Singleton(
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
    user_session_repo = providers.Factory(repos.UserSessionRepo, db_session=db_session)
    login_strategy = providers.Factory(
        services.UsernamePasswordLoginStrategy,
        user_query_repo=user_query_repo,
    )
    generate_auth_token_strategy = providers.Factory(
        services.JWTAuthTokenStrategy,
        token_service=jwt_codec,
        access_token_expires_in=settings.ACCESS_TOKEN_EXPIRES_IN,
        refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRES_IN,
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
    event_invitation_repo = providers.Factory(
        repos.EventInvitationRepo,
        db_session=db_session,
    )
    health_check_query_repo = providers.Factory(
        repos.HealthCheckQueryRepo,
        db_session=db_session,
    )
    outbox_repo = providers.Factory(
        repos.OutboxRepo,
        db_session=db_session,
    )


class UOW(containers.DeclarativeContainer):
    infra = providers.Container(Infra)
    # Events
    get_event_by_id_deps = providers.Factory(
        usecases.GetEventByIdUseCaseDeps,
        event_repo=infra.event_repo,
        event_invitation_repo=infra.event_invitation_repo,
    )
    get_event_by_id_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=get_event_by_id_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    create_event_deps = providers.Factory(
        usecases.CreateEventUseCaseDeps,
        event_repo=infra.event_repo,
    )
    create_event_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=create_event_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    delete_event_deps = providers.Factory(
        usecases.DeleteEventUseCaseDeps,
        event_repo=infra.event_repo,
    )
    delete_event_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=delete_event_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    join_event_deps = providers.Factory(
        usecases.JoinEventUseCaseDeps,
        event_repo=infra.event_repo,
        event_invitation_repo=infra.event_invitation_repo,
    )
    join_event_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=join_event_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    leave_event_deps = providers.Factory(
        usecases.LeaveEventUseCaseDeps,
        event_repo=infra.event_repo,
    )
    leave_event_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=leave_event_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    change_privacy_deps = providers.Factory(
        usecases.ChangePrivacyUseCaseDeps,
        event_repo=infra.event_repo,
    )
    change_privacy_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=change_privacy_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    # Invitations
    invite_to_event_deps = providers.Factory(
        usecases.InviteToEventUseCaseDeps,
        event_repo=infra.event_repo,
        event_invitation_repo=infra.event_invitation_repo,
    )
    invite_to_event_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=invite_to_event_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    # Auth
    login_deps = providers.Factory(
        usecases.LoginUseCaseDeps,
        user_session_repo=infra.user_session_repo,
    )
    login_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=login_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    register_deps = providers.Factory(
        usecases.RegisterUseCaseDeps,
        user_repo=infra.user_repo,
        user_session_repo=infra.user_session_repo,
    )
    register_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=register_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    logout_deps = providers.Factory(
        usecases.LogoutUseCaseDeps,
        user_session_repo=infra.user_session_repo,
    )
    logout_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=logout_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
    refresh_token_deps = providers.Factory(
        usecases.RefreshTokenUseCaseDeps,
        user_session_repo=infra.user_session_repo,
    )
    refresh_token_uow = providers.Factory(
        services.uow.SQLAlchemyUOW,
        d=refresh_token_deps,
        db_session=infra.db_session,
        outbox_repo=infra.outbox_repo,
    )
