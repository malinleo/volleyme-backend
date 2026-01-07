import typing

import pwdlib

password_hasher = pwdlib.PasswordHash.recommended()


def make_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


class PasswordValidationErrorData(typing.NamedTuple):
    message: str
    code: str


class PasswordValidationResult(typing.NamedTuple):
    is_valid: bool
    error: PasswordValidationErrorData | None = None


class PasswordValidationResults(typing.NamedTuple):
    is_valid: bool
    errors: list[PasswordValidationErrorData]


class PasswordValidator(typing.Protocol):
    def validate(self, password: str) -> PasswordValidationResults: ...


class PasswordPolicy(typing.Protocol):
    def validate(self, password: str) -> PasswordValidationResult: ...
