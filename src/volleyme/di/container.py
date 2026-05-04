from dependency_injector import containers, providers

from . import infra, usecases


class DI(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.volleyme.presentation.rest.v0_1_0.endpoints",
            "src.volleyme.presentation.rest.v0_1_0.deps",
        ],
    )
    container: providers.Self[DI] = providers.Self()
    usecases = providers.Container(usecases.Usecases)
    infra = providers.Container(infra.Infra)
