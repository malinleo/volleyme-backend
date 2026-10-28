import importlib
import pkgutil
import re

import fastapi

from src.common import usecases
from src.config import settings
from src.volleyme.di import DI
from src.volleyme.presentation.rest import endpoints, exc_handlers, v0_1_0

_VERSION_MODULE_REGEX = re.compile(r"v\d+_\d+_\d+")


def _get_api_version_modules(parent_module: str):
    return [
        importlib.import_module(f"{parent_module}.{mod_info.name}")
        for mod_info in pkgutil.iter_modules(parent_module)
        if _VERSION_MODULE_REGEX.fullmatch(mod_info.name)
    ]


container = DI()
container.wire(
    modules=[
        __name__,
        *_get_api_version_modules("src.volleyme.presentation.rest"),
        endpoints.health,
    ],
    warn_unresolved=settings.DEBUG,
)

app = fastapi.FastAPI(
    debug=settings.DEBUG,
    title="Volleyme API",
    description="API for the Volleyme project",
    version="0.0.1",
    contact={
        "name": "Leonid Malin",
        "email": "lyonyamalin84@gmail.com",
    },
)

app.include_router(v0_1_0.v0_1_0_router)
app.include_router(endpoints.health_router)

app.exception_handler(usecases.exc.UseCaseError)(exc_handlers.handle_use_case_error)
app.exception_handler(usecases.exc.NotFound)(exc_handlers.handle_not_found_error)
app.exception_handler(usecases.exc.Unauthorized)(exc_handlers.handle_unauthorized_error)
app.exception_handler(usecases.exc.PermissionDenied)(
    exc_handlers.handle_permission_denied_error,
)
