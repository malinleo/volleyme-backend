import fastapi
from src.config import settings
from src.volleyme.presentation.rest import endpoints, exc_handlers
from src.common import usecases
from src.volleyme.infra.di import DI


container = DI()
container.wire(modules=[__name__, endpoints.events])

app = fastapi.FastAPI(debug=settings.DEBUG)

app.include_router(endpoints.events_router)
app.exception_handler(usecases.exc.UseCaseError)(exc_handlers.handle_use_case_error)
app.exception_handler(usecases.exc.NotFound)(exc_handlers.handle_not_found_error)
app.exception_handler(usecases.exc.Unauthorized)(exc_handlers.handle_unauthorized_error)
app.exception_handler(usecases.exc.PermissionDenied)(
    exc_handlers.handle_permission_denied_error,
)
