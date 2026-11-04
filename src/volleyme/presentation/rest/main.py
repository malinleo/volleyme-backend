import fastapi

from src.common import usecases
from src.config import settings
from src.volleyme.di import DI
from src.volleyme.presentation.rest import endpoints, exc_handlers, v1

container = DI()
container.wire(
    modules=[
        __name__,
        v1.endpoints.auth,
        v1.endpoints.events,
        v1.endpoints.invitation,
        v1.endpoints.users,
        v1.deps,
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

app.include_router(v1.v1_router)
app.include_router(endpoints.health_router)

app.exception_handler(usecases.exc.UseCaseError)(exc_handlers.handle_use_case_error)
app.exception_handler(usecases.exc.NotFound)(exc_handlers.handle_not_found_error)
app.exception_handler(usecases.exc.Unauthorized)(exc_handlers.handle_unauthorized_error)
app.exception_handler(usecases.exc.PermissionDenied)(
    exc_handlers.handle_permission_denied_error,
)
