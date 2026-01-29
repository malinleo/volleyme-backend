import enum

from src.common import exc


class UseCaseErrorCode(enum.StrEnum):
    """All possible error codes."""

    DEFAULT = "__USE_CASE_ERROR__"
    VALIDATION_FAILED = "__USE_CASE_VALIDATION_FAILED__"
    NOT_FOUND = "__USE_CASE_NOT_FOUND__"
    UNAUTHORIZED = "__USE_CASE_UNAUTHORIZED__"
    PERMISSION_DENIED = "__USE_CASE_PERMISSION_DENIED__"
    PASSWORD_VALIDATION_FAILED = "__USE_CASE_PASSWORD_VALIDATION_FAILED__"


class UseCaseError(exc.BaseError):
    """Error in use case."""

    default_msg = "Use case error"
    code = UseCaseErrorCode.DEFAULT


class NotFound(UseCaseError):
    """Object wasn't found."""

    default_msg = "Object wasn't found"
    code = UseCaseErrorCode.NOT_FOUND


class Unauthorized(UseCaseError):
    """Unauthorized."""

    default_msg = "Unauthorized"
    code = UseCaseErrorCode.UNAUTHORIZED


class PermissionDenied(UseCaseError):
    """Permission denied."""

    default_msg = "Permission denied"
    code = UseCaseErrorCode.PERMISSION_DENIED
