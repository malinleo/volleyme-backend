import dataclasses
import enum
import typing

from . import user


class AuthTokenSchema(enum.StrEnum):
    BEARER = "Bearer"


@dataclasses.dataclass(frozen=True)
class AuthToken:
    schema: AuthTokenSchema
    access_token: str
    refresh_token: str


class AuthStrategy(typing.Protocol):
    async def authenticate(self) -> user.AuthUser | None: ...


class LoginStrategy(typing.Protocol):
    async def login(self) -> user.AuthUser | None: ...


class GenerateAuthTokenStrategy(typing.Protocol):
    async def generate(self, user: user.AuthUser) -> AuthToken: ...
