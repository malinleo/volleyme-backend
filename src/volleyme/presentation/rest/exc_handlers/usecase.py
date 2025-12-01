import fastapi
from fastapi import status

from src.common import usecases


def handle_use_case_error(
    request: fastapi.Request,
    exc: usecases.exc.UseCaseError,
) -> fastapi.responses.JSONResponse:
    """Handle use case error."""
    return fastapi.responses.JSONResponse(
        content={"detail": exc.msg, "code": exc.code},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def handle_not_found_error(
    request: fastapi.Request,
    exc: usecases.exc.NotFound,
) -> fastapi.responses.JSONResponse:
    """Handle use case error."""
    return fastapi.responses.JSONResponse(
        content={"detail": exc.msg, "code": exc.code},
        status_code=status.HTTP_404_NOT_FOUND,
    )


def handle_unauthorized_error(
    request: fastapi.Request,
    exc: usecases.exc.Unauthorized,
) -> fastapi.responses.JSONResponse:
    """Handle use case error."""
    return fastapi.responses.JSONResponse(
        content={"detail": exc.msg, "code": exc.code},
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


def handle_permission_denied_error(
    request: fastapi.Request,
    exc: usecases.exc.PermissionDenied,
) -> fastapi.responses.JSONResponse:
    """Handle use case error."""
    return fastapi.responses.JSONResponse(
        content={"detail": exc.msg, "code": exc.code},
        status_code=status.HTTP_403_FORBIDDEN,
    )
