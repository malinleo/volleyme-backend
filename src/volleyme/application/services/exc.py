import dataclasses
import enum

from src.common import exc as common_exc


class ApplicationServiceErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__APPLICATION_SERVICE_ERROR__"
    INVALID_TOKEN = "__INVALID_TOKEN__"
    EXPIRED_TOKEN = "__EXPIRED_TOKEN__"


@dataclasses.dataclass
class ApplicationServiceError(common_exc.BaseError):
    """Base error for application services."""


class InvalidToken(ApplicationServiceError):
    """Invalid token."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                common_exc.ErrorDetail(
                    code=ApplicationServiceErrorCode.INVALID_TOKEN,
                    messages=["Token is invalid"],
                )
            ],
        )


class ExpiredToken(ApplicationServiceError):
    """Expired token."""

    def __init__(self) -> None:
        super().__init__(
            details=[
                common_exc.ErrorDetail(
                    code=ApplicationServiceErrorCode.EXPIRED_TOKEN,
                    messages=["Token has expired"],
                )
            ],
        )
