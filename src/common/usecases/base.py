import collections.abc
import dataclasses

from src.common import exc as common_exc

from . import exc, validators


@dataclasses.dataclass(frozen=True, kw_only=True)
class BaseUseCase:
    def _run_validation(
        self,
        validators: collections.abc.Iterable[validators.Validator],
    ) -> None:
        validation_results = (validator.validate() for validator in validators)
        errors = tuple(result for result in validation_results if not result.is_valid)
        if errors:
            raise exc.UseCaseError(
                details=[
                    common_exc.ErrorDetail(
                        message=error.error_msg or "Validation failed",
                    )
                    for error in errors
                ],
                code=exc.UseCaseErrorCode.VALIDATION_FAILED,
            )
        return None
