import collections.abc
import re
import typing

import attrs

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
    # https://pdw.ex-parrot.com/Mail-RFC822-Address.html
    email_regex = r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    if not re.match(email_regex, value):
        raise ValueError(f"{value} is not a valid email")
