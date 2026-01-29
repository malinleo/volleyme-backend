import typing


class ValidationResult(typing.NamedTuple):
    is_valid: bool
    error_msg: str | None = None


class Validator(typing.Protocol):
    def validate(self) -> ValidationResult: ...
