from dependency_injector import containers, providers

from . import infra, usecases


class DI(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.volleyme.presentation.rest.endpoints"],
    )
    usecases = providers.Container(usecases.Usecases)
    infrastructure = providers.Container(infra.Infra)
