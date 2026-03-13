from dependency_injector import containers, providers

from src.volleyme.application import usecases

from . import infra


class Usecases(containers.DeclarativeContainer):
    infra = providers.Container(infra.Infra)
    get_event_by_id = providers.Factory(
        usecases.GetEventByIdUseCase,
        event_repo=infra.event_repo,
        event_query_repo=infra.event_query_repo,
        event_invitation_repo=infra.event_invitation_repo,
        token_service=infra.jwt_codec,
    )
    get_events = providers.Factory(
        usecases.GetEventsUseCase,
        event_query_repo=infra.event_query_repo,
    )
    create_event = providers.Factory(
        usecases.CreateEventUseCase,
        event_repo=infra.event_repo,
        event_query_repo=infra.event_query_repo,
    )
    delete_event = providers.Factory(
        usecases.DeleteEventUseCase,
        event_repo=infra.event_repo,
    )
    authenticate = providers.Factory(
        usecases.AuthUseCase,
        auth_strategy=infra.auth_strategy,
    )
    login = providers.Factory(
        usecases.AuthUseCase,
        auth_strategy=infra.login_auth_strategy,
    )
    register = providers.Factory(
        usecases.EmailPasswordRegisterUseCase,
        user_repo=infra.user_repo,
        password_validator=infra.password_validator,
    )
    join_event = providers.Factory(
        usecases.JoinEventUseCase,
        event_repo=infra.event_repo,
        event_invitation_repo=infra.event_invitation_repo,
        token_service=infra.jwt_codec,
    )
    leave_event = providers.Factory(
        usecases.LeaveEventUseCase,
        event_repo=infra.event_repo,
    )
    invite_to_event = providers.Factory(
        usecases.InviteToEventUseCase,
        event_repo=infra.event_repo,
        event_invitation_repo=infra.event_invitation_repo,
        token_service=infra.jwt_codec,
    )
    change_privacy = providers.Factory(
        usecases.ChangePrivacyUseCase,
        event_repo=infra.event_repo,
        event_query_repo=infra.event_query_repo,
    )
