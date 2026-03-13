import typing


class TokenService(typing.Protocol):
    def encode(self, payload: dict[str, typing.Any]) -> str: ...

    def decode(self, token: str | bytes) -> dict[str, typing.Any]: ...
