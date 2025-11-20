import typing

import pydantic


class BaseEntity(pydantic.BaseModel):
    """Base class for domain entities."""

    class Config:
        from_attributes = True


class AggregateRoot(BaseEntity):
    """Base class for domain aggregate roots."""


class ValueObject(pydantic.BaseModel):
    """Base class for domain value objects."""

    class Config:
        from_attributes = True


BaseEntityT = typing.TypeVar("BaseEntityT", bound=BaseEntity)
AggregateRootT = typing.TypeVar("AggregateRootT", bound=AggregateRoot)
ValueObjectT = typing.TypeVar("ValueObjectT", bound=ValueObject)
