import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.common import usecases
from src.volleyme.application import query_repos, services
from src.volleyme.domain import aggregates, repos, types
from src.volleyme.domain import exc as domain_exc

from . import exc


@dataclasses.dataclass
class AuthUseCase:
    auth_strategy: services.auth.AuthStrategy
    user_session_repo: repos.UserSessionRepo

    async def execute(self) -> services.auth.AuthUser:
        try:
            auth_user = await self.auth_strategy.authenticate()
        except services.exc.ApplicationServiceError as service_error:
            raise usecases.exc.UseCaseError.from_error(service_error) from service_error
        if not auth_user:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.NOT_FOUND,
                        messages=["User with given credentials wasn't found"],
                    )
                ],
            )
        try:
            session = await self.user_session_repo.get_session(auth_user.session_id)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to get session"],
                    )
                ],
            ) from repo_error
        if not session:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.UNAUTHORIZED,
                        messages=["Session not found"],
                    )
                ],
            )
        if not session.is_valid():
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.UNAUTHORIZED,
                        messages=["Session is invalid"],
                    )
                ],
            )
        return auth_user


@dataclasses.dataclass
class LoginUseCase:
    login_strategy: services.auth.LoginStrategy

    async def execute(self) -> services.auth.AuthUser:
        auth_user = await self.login_strategy.login()
        if not auth_user:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.INVALID_CREDENTIALS,
                        messages=["User with given credentials wasn't found"],
                    )
                ],
            )
        return auth_user


@dataclasses.dataclass
class RegisterUseCase:
    user_repo: repos.UserRepo
    user_query_repo: query_repos.UserQueryRepo
    user_session_repo: repos.UserSessionRepo
    password_validator: services.auth.PasswordValidator
    refresh_token_expires_in: int

    async def execute(
        self,
        username: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
    ) -> services.auth.AuthUser:
        if await self.user_query_repo.get_user_auth_info(username):
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.USER_ALREADY_EXISTS,
                        messages=["User with given username already exists"],
                    )
                ],
            )
        validation_results = self.password_validator.validate(password)
        if not validation_results.is_valid:
            raise exc.PasswordValidationFailed(validation_results)
        password_hash = aggregates.PasswordHash(
            value=services.auth.make_password_hash(password),
        )
        try:
            user = aggregates.User.create(
                username=username,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url,
            )
        except domain_exc.DomainError as domain_error:
            raise usecases.exc.UseCaseError.from_error(domain_error) from domain_error
        try:
            user = await self.user_repo.save_user(user)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to register user"],
                    )
                ],
            ) from repo_error
        try:
            session = aggregates.UserSession.create(
                user_id=user.id,
                expires_at=datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(seconds=self.refresh_token_expires_in),
            )
        except domain_exc.DomainError as domain_error:
            raise usecases.exc.UseCaseError.from_error(domain_error) from domain_error
        try:
            session = await self.user_session_repo.save_session(session, create=True)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to register user"],
                    )
                ],
            ) from repo_error
        return services.auth.AuthUser(id=user.id, session_id=session.id)


@dataclasses.dataclass
class LogoutUseCase:
    user_session_repo: repos.UserSessionRepo

    async def execute(self, user: services.auth.AuthUser) -> None:
        try:
            session = await self.user_session_repo.get_session(user.session_id)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to logout user"],
                    )
                ],
            ) from repo_error
        if not session:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.NOT_FOUND,
                        messages=["Session not found"],
                    )
                ],
            )
        session.revoke()
        try:
            await self.user_session_repo.save_session(session)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to logout user"],
                    )
                ],
            ) from repo_error


@dataclasses.dataclass
class RefreshTokenUseCase:
    token_service: services.token.TokenService
    user_session_repo: repos.UserSessionRepo
    refresh_token_expires_in: int

    async def execute(self, refresh_token: str | bytes) -> services.auth.AuthUser:
        try:
            token_payload = self.token_service.decode(refresh_token)
        except services.exc.ApplicationServiceError as error:
            raise usecases.exc.UseCaseError.from_error(error) from error
        if token_payload["typ"] != "refresh":
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.INVALID_TOKEN_TYPE,
                        messages=["Invalid token type"],
                    )
                ],
            )
        user = services.auth.AuthUser(
            id=types.UserId(uuid.UUID(token_payload["sub"])),
            session_id=types.UserSessionId(uuid.UUID(token_payload["sid"])),
        )
        try:
            session = await self.user_session_repo.get_session(user.session_id)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to refresh user"],
                    )
                ],
            ) from repo_error
        if not session:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.NOT_FOUND,
                        messages=["Session not found"],
                    )
                ],
            )
        if not session.is_valid():
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.SESSION_INVALID,
                        messages=["Session is invalid"],
                    )
                ],
            )
        session.revoke()
        try:
            await self.user_session_repo.save_session(session)
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to revoke old session"],
                    )
                ],
            ) from repo_error
        new_session = aggregates.UserSession.create(
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=self.refresh_token_expires_in),
        )
        try:
            new_session = await self.user_session_repo.save_session(
                new_session,
                create=True,
            )
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to save new session"],
                    )
                ],
            ) from repo_error
        return services.auth.AuthUser(id=user.id, session_id=new_session.id)
