import enum

from src.common import exc as common_exc


class AuthErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__AUTH_ERROR__"
    INVALID_TOKEN = "__INVALID_TOKEN__"
    EXPIRED_TOKEN = "__EXPIRED_TOKEN__"


class AuthError(common_exc.BaseError):
    """Error in authentication."""

    def __init__(self, detail: common_exc.ErrorDetail) -> None:
        super().__init__(
            detail=common_exc.ErrorDetail(
                code=AuthErrorCode.DEFAULT,
                messages=["Authentication error"],
            ),
        )


class InvalidToken(AuthError):
    """Invalid token."""

    def __init__(self) -> None:
        super().__init__(
            detail=common_exc.ErrorDetail(
                code=AuthErrorCode.INVALID_TOKEN,
                messages=["Token is invalid"],
            ),
        )


class ExpiredToken(AuthError):
    """Expired token."""

    def __init__(self) -> None:
        super().__init__(
            detail=common_exc.ErrorDetail(
                code=AuthErrorCode.EXPIRED_TOKEN,
                messages=["Token has expired"],
            ),
        )
