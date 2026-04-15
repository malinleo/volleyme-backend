import enum

from src.common import exc as common_exc
from src.volleyme.application.services import exc


class AuthErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__AUTH_ERROR__"
    INVALID_TOKEN = "__INVALID_TOKEN__"
    EXPIRED_TOKEN = "__EXPIRED_TOKEN__"
    INVALID_TOKEN_TYPE = "__INVALID_TOKEN_TYPE__"


class AuthError(exc.ApplicationServiceError):
    """Error in authentication."""


class InvalidToken(AuthError):
    """Invalid token."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                common_exc.ErrorDetail(
                    code=AuthErrorCode.INVALID_TOKEN,
                    messages=["Token is invalid"],
                )
            ],
        )


class ExpiredToken(AuthError):
    """Expired token."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                common_exc.ErrorDetail(
                    code=AuthErrorCode.EXPIRED_TOKEN,
                    messages=["Token has expired"],
                )
            ],
        )
