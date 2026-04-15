import dataclasses
import typing

import jwt

from src.volleyme.application import services


@dataclasses.dataclass(frozen=True)
class JWTCodecService(services.token.TokenService):
    public_key: str
    private_key: str
    algorithm: str = "ES256"

    def encode(
        self,
        payload: dict[str, typing.Any],
        extra_headers: dict[str, typing.Any] | None = None,
    ) -> str:
        extra_headers = extra_headers or {}
        return jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm,
            headers={**extra_headers, "alg": self.algorithm},
        )

    def decode(self, token: str | bytes) -> dict[str, typing.Any]:
        if isinstance(token, bytes):
            token = token.decode()
        try:
            return jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True},
            )
        except jwt.exceptions.ExpiredSignatureError as error:
            raise services.auth.exc.ExpiredToken() from error
        except jwt.exceptions.PyJWTError as error:
            raise services.auth.exc.InvalidToken() from error
