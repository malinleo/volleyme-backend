import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.common import result
from src.volleyme.application import query_repos, services
from src.volleyme.domain import types

from . import token


@dataclasses.dataclass(frozen=True)
class UsernamePasswordCredentials:
    username: str
    password: str


@dataclasses.dataclass(frozen=True)
class JWTCredentials:
    token: str


@dataclasses.dataclass
class JWTAuthStrategy(services.auth.AuthStrategy):
    credentials: JWTCredentials
    token_service: token.JWTCodecService

    async def authenticate(
        self,
    ) -> result.Result[services.auth.AuthUser, services.auth.exc.AuthError]:
        payload = self.token_service.decode(self.credentials.token)
        if payload["typ"] != "access":
            error = services.auth.exc.AuthError(
                details=[
                    common_exc.ErrorDetail(
                        code=services.auth.exc.AuthErrorCode.INVALID_TOKEN_TYPE,
                        messages=["Invalid token type"],
                    )
                ],
            )
            return result.Err(errors=[error])
        return result.Ok(
            services.auth.AuthUser(
                id=types.UserId(uuid.UUID(payload["sub"])),
                session_id=types.UserSessionId(uuid.UUID(payload["sid"])),
            ),
        )


@dataclasses.dataclass(frozen=True)
class UsernamePasswordLoginStrategy(services.auth.LoginStrategy):
    credentials: UsernamePasswordCredentials
    user_query_repo: query_repos.UserQueryRepo

    async def login(self) -> services.auth.LoginResult | None:
        user_auth_info = await self.user_query_repo.get_user_auth_info(
            self.credentials.username,
        )
        if not user_auth_info or not services.auth.verify_password(
            self.credentials.password,
            user_auth_info.password,
        ):
            return None
        return services.auth.LoginResult(id=user_auth_info.id)


@dataclasses.dataclass
class JWTAuthTokenStrategy(services.auth.GenerateAuthTokenStrategy):
    token_service: token.JWTCodecService
    access_token_expires_in: int
    refresh_token_expires_in: int

    async def generate(self, user: services.auth.AuthUser) -> services.auth.AuthToken:
        now = int(datetime.datetime.now(datetime.UTC).timestamp())
        return services.auth.AuthToken(
            schema=services.auth.AuthTokenSchema.BEARER,
            access_token=self.token_service.encode(
                {
                    "sub": str(user.id),
                    "sid": str(user.session_id),
                    "iat": now,
                    "exp": now + self.access_token_expires_in,
                    "typ": "access",
                },
            ),
            refresh_token=self.token_service.encode(
                {
                    "sub": str(user.id),
                    "sid": str(user.session_id),
                    "iat": now,
                    "exp": now + self.refresh_token_expires_in,
                    "typ": "refresh",
                },
            ),
        )
