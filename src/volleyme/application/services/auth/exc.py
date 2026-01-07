import enum

from src.common import exc


class AuthErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__AUTH_ERROR__"
    INVALID_TOKEN = "__INVALID_TOKEN__"
    EXPIRED_TOKEN = "__EXPIRED_TOKEN__"


class AuthError(exc.BaseError):
    """Error in authentication."""

    default_msg = "Authentication error"
    code = AuthErrorCode.DEFAULT


class InvalidToken(AuthError):
    """Invalid token."""

    default_msg = "Token is invalid"
    code = AuthErrorCode.INVALID_TOKEN


class ExpiredToken(AuthError):
    """Expired token."""

    default_msg = "Token has expired"
    code = AuthErrorCode.EXPIRED_TOKEN
