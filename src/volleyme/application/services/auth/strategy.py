import dataclasses
import enum
import typing

from src.common import result
from src.volleyme.domain import types

from . import exc, user


class AuthTokenSchema(enum.StrEnum):
    BEARER = "Bearer"


@dataclasses.dataclass(frozen=True)
class AuthToken:
    schema: AuthTokenSchema
    access_token: str
    refresh_token: str


class AuthStrategy(typing.Protocol):
    async def authenticate(self) -> result.Result[user.AuthUser, exc.AuthError]: ...


@dataclasses.dataclass(frozen=True)
class LoginResult:
    id: types.UserId


class LoginStrategy(typing.Protocol):
    async def login(self) -> LoginResult | None: ...


class GenerateAuthTokenStrategy(typing.Protocol):
    async def generate(self, user: user.AuthUser) -> AuthToken: ...
