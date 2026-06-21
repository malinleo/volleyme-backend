from dependency_injector import containers, providers

from src.config import settings
from src.volleyme.application import services, usecases

from . import infra as infra_module


class Services(containers.DeclarativeContainer):
    infra = providers.Container(infra_module.Infra)
    uow = providers.Container(infra_module.UOW, infra=infra)
    event_created_handler = providers.Factory(
        services.events.EventCreatedHandlerProtocol,
        uow=uow.event_created_handler_uow,
    )


class Usecases(containers.DeclarativeContainer):
    infra = providers.Container(infra_module.Infra)
    uow = providers.Container(infra_module.UOW, infra=infra)
    # Events
    get_event_by_id = providers.Factory(
        usecases.GetEventByIdUseCase,
        uow=uow.get_event_by_id_uow,
        event_query_repo=infra.event_query_repo,
        token_service=infra.jwt_codec,
    )
    get_events = providers.Factory(
        usecases.GetEventsUseCase,
        event_query_repo=infra.event_query_repo,
    )
    create_event = providers.Factory(
        usecases.CreateEventUseCase,
        uow=uow.create_event_uow,
        event_query_repo=infra.event_query_repo,
    )
    delete_event = providers.Factory(
        usecases.DeleteEventUseCase,
        uow=uow.delete_event_uow,
    )
    join_event = providers.Factory(
        usecases.JoinEventUseCase,
        uow=uow.join_event_uow,
        token_service=infra.jwt_codec,
    )
    leave_event = providers.Factory(
        usecases.LeaveEventUseCase,
        uow=uow.leave_event_uow,
    )
    change_privacy = providers.Factory(
        usecases.ChangePrivacyUseCase,
        uow=uow.change_privacy_uow,
        event_query_repo=infra.event_query_repo,
    )
    # Invitations
    invite_to_event = providers.Factory(
        usecases.InviteToEventUseCase,
        uow=uow.invite_to_event_uow,
        token_service=infra.jwt_codec,
    )
    # Auth
    authenticate = providers.Factory(
        usecases.AuthUseCase,
        user_session_repo=infra.user_session_repo,
        auth_strategy=infra.auth_strategy,
    )
    login = providers.Factory(
        usecases.LoginUseCase,
        uow=uow.login_uow,
        login_strategy=infra.login_strategy,
        refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRES_IN,
    )
    register = providers.Factory(
        usecases.RegisterUseCase,
        uow=uow.register_uow,
        user_query_repo=infra.user_query_repo,
        password_validator=infra.password_validator,
        refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRES_IN,
    )
    logout = providers.Factory(
        usecases.LogoutUseCase,
        uow=uow.logout_uow,
    )
    refresh = providers.Factory(
        usecases.RefreshTokenUseCase,
        uow=uow.refresh_token_uow,
        token_service=infra.jwt_codec,
        refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRES_IN,
    )
    # Health Check
    health_check = providers.Factory(
        usecases.HealthCheckUseCase,
        health_check_query_repo=infra.health_check_query_repo,
    )
