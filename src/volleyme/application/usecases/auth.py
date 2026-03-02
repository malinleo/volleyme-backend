import dataclasses

from src.common import exc as common_exc
from src.common import usecases
from src.volleyme.application import services
from src.volleyme.domain import aggregates, repos


@dataclasses.dataclass
class AuthUseCase:
    auth_strategy: services.AuthStrategy

    async def execute(self) -> services.AuthUser:
        try:
            auth_user = await self.auth_strategy.authenticate()
        except services.exc.AuthError as auth_error:
            raise usecases.exc.UseCaseError(
                detail=common_exc.ErrorDetail(
                    code=usecases.exc.UseCaseErrorCode.DEFAULT,
                    messages=["Failed to authenticate"],
                ),
            ) from auth_error
        if not auth_user:
            raise usecases.exc.UseCaseError(
                detail=common_exc.ErrorDetail(
                    code=usecases.exc.UseCaseErrorCode.NOT_FOUND,
                    messages=["User with given credentials wasn't found"],
                ),
            )
        return auth_user


@dataclasses.dataclass
class EmailPasswordRegisterUseCase:
    user_repo: repos.UserRepo
    password_validator: services.auth.PasswordValidator

    async def execute(self, email: str, password: str) -> services.AuthUser:
        validation_results = self.password_validator.validate(password)
        if not validation_results.is_valid:
            raise usecases.exc.UseCaseError(
                detail=common_exc.ErrorDetail(
                    code=usecases.exc.UseCaseErrorCode.PASSWORD_VALIDATION_FAILED,
                    messages=["Password validation failed"],
                    fields={
                        "password": common_exc.FieldErrorDetail(
                            code=usecases.exc.UseCaseErrorCode.PASSWORD_VALIDATION_FAILED,
                            messages=[
                                error.message for error in validation_results.errors
                            ],
                        ),
                    },
                ),
            )
        password_hash = aggregates.PasswordHash(
            value=services.make_password_hash(password),
        )
        user = await self.user_repo.save_user(
            aggregates.User(email=email, password_hash=password_hash),
        )
        return services.AuthUser(id=user.id)
