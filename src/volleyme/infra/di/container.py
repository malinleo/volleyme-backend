from dependency_injector import containers, providers

from . import infra, usecases


class DI(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.volleyme.presentation.rest.endpoints",
            "src.volleyme.presentation.rest.deps",
        ],
    )
    container = providers.Self()
    usecases = providers.Container(usecases.Usecases)
    infra = providers.Container(infra.Infra)
