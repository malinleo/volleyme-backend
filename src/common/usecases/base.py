import collections.abc
import dataclasses

from src.common import exc as common_exc

from . import exc, validators


@dataclasses.dataclass(frozen=True, kw_only=True)
class BaseUseCase:
    def _get_validation_errors(
        self,
        validators: collections.abc.Iterable[validators.Validator],
    ) -> tuple[validators.ValidationResult, ...]:
        validation_results = (validator.validate() for validator in validators)
        return tuple(result for result in validation_results if not result.is_valid)

    def _run_validation(
        self,
        validators: collections.abc.Iterable[validators.Validator],
    ) -> None:
        errors = self._get_validation_errors(validators)
        if not errors:
            return None
        raise exc.UseCaseError(
            details=[
                common_exc.ErrorDetail(
                    code=exc.UseCaseErrorCode.VALIDATION_FAILED,
                    messages=[
                        error.error_msg or "Validation failed" for error in errors
                    ],
                )
            ]
        )
