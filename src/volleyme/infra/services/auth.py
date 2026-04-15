import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.volleyme.application import query_repos, services
from src.volleyme.domain import aggregates, repos, types

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

    async def authenticate(self) -> services.auth.AuthUser | None:
        payload = self.token_service.decode(self.credentials.token)
        if payload["typ"] != "access":
            raise services.auth.exc.AuthError(
                details=[
                    common_exc.ErrorDetail(
                        code=services.auth.exc.AuthErrorCode.INVALID_TOKEN_TYPE,
                        messages=["Invalid token type"],
                    )
                ],
            )
        return services.auth.AuthUser(
            id=types.UserId(uuid.UUID(payload["sub"])),
            session_id=types.UserSessionId(uuid.UUID(payload["sid"])),
        )


@dataclasses.dataclass(frozen=True)
class UsernamePasswordLoginStrategy(services.auth.LoginStrategy):
    credentials: UsernamePasswordCredentials
    user_query_repo: query_repos.UserQueryRepo
    user_session_repo: repos.UserSessionRepo
    refresh_token_expires_in: int

    async def login(self) -> services.auth.AuthUser | None:
        user_auth_info = await self.user_query_repo.get_user_auth_info(
            self.credentials.username,
        )
        if not user_auth_info or not services.auth.verify_password(
            self.credentials.password,
            user_auth_info.password,
        ):
            return None
        session = aggregates.UserSession.create(
            user_id=user_auth_info.id,
            expires_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=self.refresh_token_expires_in),
        )
        try:
            session = await self.user_session_repo.save_session(session, create=True)
        except repos.exc.RepoError as repo_error:
            raise services.exc.ApplicationServiceError(
                details=[
                    common_exc.ErrorDetail(
                        code=services.exc.ApplicationServiceErrorCode.DEFAULT,
                        messages=["Failed to login user"],
                    )
                ],
            ) from repo_error
        return services.auth.AuthUser(id=user_auth_info.id, session_id=session.id)


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
