import typing

from . import user


class AuthStrategy(typing.Protocol):
    async def authenticate(self) -> user.AuthUser | None: ...
