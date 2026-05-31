import dataclasses
import datetime
import uuid

from src.common import exc as common_exc
from src.common import result, usecases
from src.volleyme.application import query_repos, services
from src.volleyme.domain import aggregates, repos, types

from . import exc


@dataclasses.dataclass
class AuthUseCase:
    user_session_repo: repos.UserSessionRepo
    auth_strategy: services.auth.AuthStrategy

    @exc.wrap_errors
    async def execute(self) -> services.auth.AuthUser:
        auth_result = await self.auth_strategy.authenticate()
        match auth_result:
            case result.Err():
                raise usecases.exc.Unauthorized(
                    message="Failed to authenticate",
                )
        auth_user = auth_result.value
        if not auth_user:
            raise usecases.exc.Unauthorized(
                message="User with given credentials wasn't found",
            )
        session = await self.user_session_repo.get_session(auth_user.session_id)
        if not session:
            raise usecases.exc.Unauthorized(message="Session not found")
        if not session.is_valid():
            raise usecases.exc.Unauthorized(message="Session is invalid")
        return auth_user


@dataclasses.dataclass(frozen=True)
class LoginUseCaseDeps:
    user_session_repo: repos.UserSessionRepo


@dataclasses.dataclass
class LoginUseCase:
    uow: services.uow.UOW[LoginUseCaseDeps]
    login_strategy: services.auth.LoginStrategy
    refresh_token_expires_in: int

    @exc.wrap_errors
    async def execute(self) -> services.auth.AuthUser:
        login_result = await self.login_strategy.login()
        if not login_result:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.INVALID_CREDENTIALS,
                        messages=["User with given credentials wasn't found"],
                    )
                ],
            )
        session = aggregates.UserSession.create(
            user_id=login_result.id,
            expires_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=self.refresh_token_expires_in),
        )
        session = await self.uow.d.user_session_repo.save_session(session, create=True)
        await self.uow.commit()
        return services.auth.AuthUser(id=login_result.id, session_id=session.id)


@dataclasses.dataclass(frozen=True)
class RegisterUseCaseDeps:
    user_repo: repos.UserRepo
    user_session_repo: repos.UserSessionRepo


@dataclasses.dataclass
class RegisterUseCase:
    uow: services.uow.UOW[RegisterUseCaseDeps]
    user_query_repo: query_repos.UserQueryRepo
    password_validator: services.auth.PasswordValidator
    refresh_token_expires_in: int

    @exc.wrap_errors
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
        user = aggregates.User.create(
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
        )
        user = await self.uow.d.user_repo.save_user(user)
        session = aggregates.UserSession.create(
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=self.refresh_token_expires_in),
        )
        session = await self.uow.d.user_session_repo.save_session(session, create=True)
        await self.uow.commit()
        return services.auth.AuthUser(id=user.id, session_id=session.id)


@dataclasses.dataclass(frozen=True)
class LogoutUseCaseDeps:
    user_session_repo: repos.UserSessionRepo


@dataclasses.dataclass
class LogoutUseCase:
    uow: services.uow.UOW[LogoutUseCaseDeps]

    @exc.wrap_errors
    async def execute(self, user: services.auth.AuthUser) -> None:
        session = await self.uow.d.user_session_repo.get_session(user.session_id)
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
        await self.uow.d.user_session_repo.save_session(session)
        await self.uow.commit()


@dataclasses.dataclass(frozen=True)
class RefreshTokenUseCaseDeps:
    user_session_repo: repos.UserSessionRepo


@dataclasses.dataclass
class RefreshTokenUseCase:
    uow: services.uow.UOW[RefreshTokenUseCaseDeps]
    token_service: services.token.TokenService
    refresh_token_expires_in: int

    @exc.wrap_errors
    async def execute(self, refresh_token: str | bytes) -> services.auth.AuthUser:
        token_payload = self.token_service.decode(refresh_token)
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
        session = await self.uow.d.user_session_repo.get_session(user.session_id)
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
        await self.uow.d.user_session_repo.save_session(session)
        new_session = aggregates.UserSession.create(
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=self.refresh_token_expires_in),
        )
        try:
            new_session = await self.uow.d.user_session_repo.save_session(
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
        await self.uow.commit()
        return services.auth.AuthUser(id=user.id, session_id=new_session.id)
