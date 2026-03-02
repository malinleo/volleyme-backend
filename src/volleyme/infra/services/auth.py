import dataclasses
import datetime
import typing
import uuid

import jwt

from src.volleyme.application import query_repos, services
from src.volleyme.domain import types
from src.volleyme.presentation import auth


@dataclasses.dataclass(frozen=True)
class EmailPasswordCredentials:
    email: str
    password: str


@dataclasses.dataclass(frozen=True)
class JWTCredentials:
    token: str


@dataclasses.dataclass(frozen=True)
class JWTCodecService:
    public_key: str
    private_key: str
    algorithm: str = "RS256"

    def encode(self, payload: dict[str, typing.Any]) -> str:
        return jwt.encode(
            payload,
            self.private_key,
            algorithm=self.algorithm,
            headers={"alg": self.algorithm, "typ": "JWT"},
        )

    def decode(self, token: str | bytes) -> dict[str, typing.Any]:
        if isinstance(token, bytes):
            token = token.decode()
        return jwt.decode(
            token,
            self.public_key,
            algorithms=[self.algorithm],
            options={"verify_exp": True},
        )


@dataclasses.dataclass
class JWTAuthStrategy(services.AuthStrategy):
    credentials: JWTCredentials
    token_service: JWTCodecService

    async def authenticate(self) -> services.AuthUser | None:
        try:
            payload = self.token_service.decode(self.credentials.token)
        except jwt.exceptions.ExpiredSignatureError:
            raise services.exc.ExpiredToken()
        except jwt.exceptions.PyJWTError:
            raise services.exc.InvalidToken()
        return services.AuthUser(id=types.UserId(uuid.UUID(payload["sub"])))


@dataclasses.dataclass(frozen=True)
class EmailPasswordAuthStrategy(services.AuthStrategy):
    credentials: EmailPasswordCredentials
    user_query_repo: query_repos.UserQueryRepo

    async def authenticate(self) -> services.AuthUser | None:
        user_auth_info = await self.user_query_repo.get_user_auth_info(
            self.credentials.email
        )
        if user_auth_info and services.verify_password(
            self.credentials.password,
            user_auth_info.password,
        ):
            return services.AuthUser(id=user_auth_info.id)
        return None


@dataclasses.dataclass
class JWTAuthTokenStrategy(auth.GenerateAuthTokenStrategy):
    token_service: JWTCodecService
    expires_in: int

    async def generate(self, user: services.AuthUser) -> auth.AuthToken:
        now = int(datetime.datetime.now(datetime.UTC).timestamp())
        return auth.AuthToken(
            schema=auth.AuthTokenSchema.BEARER,
            token=self.token_service.encode(
                {
                    "sub": str(user.id),
                    "iat": now,
                    "exp": now + self.expires_in,
                }
            ),
        )
