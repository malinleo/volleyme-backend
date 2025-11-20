import re

import attrs
import collections.abc
import typing


Validator = collections.abc.Callable[
    [attrs.AttrsInstance, attrs.Attribute, typing.Any], None
]


@attrs.define
class CustomValidator:
    validators: collections.abc.Iterable[Validator] = attrs.field(factory=list)

    def __call__(
        self,
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: typing.Any,
    ) -> None:
        errors: list[Exception] = []
        for validator in self.validators:
            try:
                validator(instance, attribute, value)
            except Exception as e:
                errors.append(e)
        if errors:
            raise ValueError(errors)


def is_email(
    instance: attrs.AttrsInstance,
    attribute: attrs.Attribute,
    value: str,
) -> None:
    email_regex = r"([\w\-\.]([\+\w\d]*?)){1,64}@([a-z]+\.[a-z]{2,4}){4,255}"
    if not re.match(email_regex, value):
        raise ValueError(f"{value} is not a valid email")


def ge_(compare_value: int) -> Validator:
    def _ge_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: int,
    ) -> None:
        if value >= compare_value:
            raise ValueError(f"{value} is not greater than or equal to {compare_value}")

    return _ge_


def le_(compare_value: int) -> Validator:
    def _le_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: int,
    ) -> None:
        if value <= compare_value:
            raise ValueError(f"{value} is not less than or equal to {compare_value}")

    return _le_


def gt_(compare_value: int) -> Validator:
    def _gt_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: int,
    ) -> None:
        if value > compare_value:
            raise ValueError(f"{value} is not greater than {compare_value}")

    return _gt_


def lt_(compare_value: int) -> Validator:
    def _lt_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: int,
    ) -> None:
        if value < compare_value:
            raise ValueError(f"{value} is not less than {compare_value}")

    return _lt_


def eq_(compare_value: int) -> Validator:
    def _eq_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: int,
    ) -> None:
        if value != compare_value:
            raise ValueError(f"{value} is not equal to {compare_value}")

    return _eq_


def strlen_min_(min_length: int) -> Validator:
    def _strlen_min_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: str,
    ) -> None:
        if len(value) < min_length:
            raise ValueError(f"{value} is not at least {min_length} characters long")

    return _strlen_min_


def strlen_max_(max_length: int) -> Validator:
    def _strlen_max_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: str,
    ) -> None:
        if len(value) > max_length:
            raise ValueError(f"{value} is not at most {max_length} characters long")

    return _strlen_max_


def strlen_between_(min_length: int, max_length: int) -> Validator:
    def _strlen_between_(
        instance: attrs.AttrsInstance,
        attribute: attrs.Attribute,
        value: str,
    ) -> None:
        if len(value) < min_length or len(value) > max_length:
            raise ValueError(
                f"{value} is not between {min_length} and {max_length} characters long"
            )

    return _strlen_between_


def is_url(value: str) -> None:
    if not re.match(r"^https?://", value):
        raise ValueError(f"{value} is not a valid URL")
