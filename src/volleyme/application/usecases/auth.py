import dataclasses

from src.common import exc as common_exc
from src.common import usecases
from src.volleyme.application import services
from src.volleyme.domain import aggregates, repos

from . import exc


@dataclasses.dataclass
class AuthUseCase:
    auth_strategy: services.auth.AuthStrategy

    async def execute(self) -> services.auth.AuthUser:
        try:
            auth_user = await self.auth_strategy.authenticate()
        except services.auth.exc.AuthError as auth_error:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.DEFAULT,
                        messages=["Failed to authenticate"],
                    )
                ],
            ) from auth_error
        if not auth_user:
            raise usecases.exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases.exc.UseCaseErrorCode.NOT_FOUND,
                        messages=["User with given credentials wasn't found"],
                    )
                ],
            )
        return auth_user


@dataclasses.dataclass
class EmailPasswordRegisterUseCase:
    user_repo: repos.UserRepo
    password_validator: services.auth.PasswordValidator

    async def execute(self, email: str, password: str) -> services.auth.AuthUser:
        validation_results = self.password_validator.validate(password)
        if not validation_results.is_valid:
            raise exc.PasswordValidationFailed(validation_results)
        password_hash = aggregates.PasswordHash(
            value=services.auth.make_password_hash(password),
        )
        try:
            user = await self.user_repo.save_user(
                aggregates.User(email=email, password_hash=password_hash),
            )
        except repos.exc.RepoError as repo_error:
            raise usecases.exc.UseCaseError.from_error(repo_error) from repo_error
        return services.auth.AuthUser(id=user.id)
