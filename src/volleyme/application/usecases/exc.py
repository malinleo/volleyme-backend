import collections.abc
import typing

from src.common import exc as common_exc
from src.common.usecases import exc as usecases_exc
from src.config import settings
from src.volleyme.application import services
from src.volleyme.application.services import exc as services_exc
from src.volleyme.domain import exc as domain_exc
from src.volleyme.domain.repos import exc as repos_exc


def wrap_errors(
    func: typing.Callable[
        ...,
        collections.abc.Coroutine[typing.Any, typing.Any, typing.Any],
    ],
) -> typing.Callable[
    ...,
    collections.abc.Coroutine[typing.Any, typing.Any, typing.Any],
]:
    async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        try:
            return await func(*args, **kwargs)
        except (
            services_exc.ApplicationServiceError,
            domain_exc.DomainError,
        ) as e:
            raise usecases_exc.UseCaseError.from_error(e) from e
        except repos_exc.RepoError as repo_error:
            if settings.DEBUG:
                raise usecases_exc.UseCaseError.from_error(repo_error) from repo_error
            raise usecases_exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        code=usecases_exc.UseCaseErrorCode.DEFAULT,
                        messages=["Repository error"],
                    )
                ],
            ) from repo_error

    return wrapper


class PasswordValidationFailed(usecases_exc.UseCaseError):
    """Password validation failed."""

    def __init__(
        self,
        validation_results: services.auth.PasswordValidationResults,
    ) -> None:
        super().__init__(
            details=[
                common_exc.ErrorDetail(
                    code=usecases_exc.UseCaseErrorCode.PASSWORD_VALIDATION_FAILED,
                    messages=["Password validation failed"],
                    fields={
                        "password": common_exc.FieldErrorDetail(
                            code=usecases_exc.UseCaseErrorCode.PASSWORD_VALIDATION_FAILED,
                            messages=[
                                error.message for error in validation_results.errors
                            ],
                        ),
                    },
                )
            ],
        )
