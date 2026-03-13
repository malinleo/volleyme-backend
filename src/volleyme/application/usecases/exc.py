from src.common import exc as common_exc
from src.common.usecases import exc as usecases_exc
from src.volleyme.application import services


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
