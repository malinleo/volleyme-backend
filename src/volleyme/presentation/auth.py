import dataclasses
import enum
import typing

from src.volleyme.application import services


class AuthTokenSchema(enum.StrEnum):
    BEARER = "Bearer"


@dataclasses.dataclass(frozen=True)
class AuthToken:
    schema: AuthTokenSchema
    token: str


class GenerateAuthTokenStrategy(typing.Protocol):
    async def generate(self, user: services.auth.AuthUser) -> AuthToken: ...
