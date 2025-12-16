import dataclasses
import enum
import typing

import pwdlib

from src.common import exc
from src.volleyme.domain import types


@dataclasses.dataclass
class AuthUser:
    id: types.UserId


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


class AuthStrategy(typing.Protocol):
    async def authenticate(self) -> AuthUser | None: ...


password_hash = pwdlib.PasswordHash.recommended()


def make_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
