import collections.abc
import dataclasses

from src.volleyme.application import services


class PasswordValidator(services.auth.PasswordValidator):
    def __init__(
        self,
        policies: collections.abc.Iterable[services.auth.PasswordPolicy],
    ):
        self._policies = policies

    def validate(self, password: str) -> services.auth.PasswordValidationResults:
        validation_results = tuple(
            policy.validate(password) for policy in self._policies
        )
        is_valid = all(result.is_valid for result in validation_results)
        errors: list[services.auth.PasswordValidationErrorData] = []
        if not is_valid:
            for result in validation_results:
                if not result.is_valid and result.error:
                    errors.append(result.error)

        return services.auth.PasswordValidationResults(is_valid=is_valid, errors=errors)


@dataclasses.dataclass(frozen=True)
class MinLength(services.auth.PasswordPolicy):
    min_length: int

    def validate(self, password: str) -> services.auth.PasswordValidationResult:
        if len(password) >= self.min_length:
            return services.auth.PasswordValidationResult(is_valid=True)
        return services.auth.PasswordValidationResult(
            is_valid=False,
            error=services.auth.PasswordValidationErrorData(
                message=f"Password must be at least {self.min_length} characters long",
                code="min_length",
            ),
        )


@dataclasses.dataclass(frozen=True)
class MaxLength(services.auth.PasswordPolicy):
    max_length: int

    def validate(self, password: str) -> services.auth.PasswordValidationResult:
        if len(password) <= self.max_length:
            return services.auth.PasswordValidationResult(is_valid=True)
        return services.auth.PasswordValidationResult(
            is_valid=False,
            error=services.auth.PasswordValidationErrorData(
                message=f"Password must be at most {self.max_length} characters long",
                code="max_length",
            ),
        )


@dataclasses.dataclass(frozen=True)
class ContainsChars(services.auth.PasswordPolicy):
    chars: set[str]
    chars_type_name: str
    error_code: str

    def validate(self, password: str) -> services.auth.PasswordValidationResult:
        for symbol in password:
            if symbol in self.chars:
                return services.auth.PasswordValidationResult(is_valid=True)
        return services.auth.PasswordValidationResult(
            is_valid=False,
            error=services.auth.PasswordValidationErrorData(
                message=f"Password must contain at least one {self.chars_type_name}",
                code=self.error_code,
            ),
        )
