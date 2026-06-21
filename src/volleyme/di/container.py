from dependency_injector import containers, providers

from . import app, infra


class DI(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.volleyme.presentation.rest.endpoints",
            "src.volleyme.presentation.rest.deps",
            "src.volleyme.infra.services.events",
        ],
    )
    container: DI = providers.Self()  # type: ignore
    infra: infra.Infra = providers.Container(infra.Infra)  # type: ignore
    usecases: app.Usecases = providers.Container(app.Usecases, infra=infra)  # type: ignore
    services: app.Services = providers.Container(app.Services, infra=infra)  # type: ignore
