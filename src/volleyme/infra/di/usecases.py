from dependency_injector import containers, providers

from src.volleyme.application import usecases

from . import infra


class Usecases(containers.DeclarativeContainer):
    infra = providers.Container(infra.Infra)
    get_event_by_id = providers.Factory(
        usecases.GetEventByIdUseCase,
        event_query_repo=infra.event_query_repo,
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
