from dependency_injector import containers, providers

from src.volleyme.application import usecases

from . import infra


class Usecases(containers.DeclarativeContainer):
    infra = providers.Container(infra.Infra)
    get_event_by_id = providers.Factory(
        usecases.GetEventByIdUseCase,
        event_repo=infra.event_repo,
    )
    get_events = providers.Factory(
        usecases.GetEventsUseCase,
        event_repo=infra.event_repo,
    )
    create_event = providers.Factory(
        usecases.CreateEventUseCase,
        event_repo=infra.event_repo,
    )
