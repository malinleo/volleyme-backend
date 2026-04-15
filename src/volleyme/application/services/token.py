import typing


class TokenService(typing.Protocol):
    def encode(
        self,
        payload: dict[str, typing.Any],
        extra_headers: dict[str, typing.Any] | None = None,
    ) -> str: ...

    def decode(self, token: str | bytes) -> dict[str, typing.Any]: ...
