import abc
import collections.abc
import typing

KeyT = typing.TypeVar("KeyT", bound=typing.Any)
KeyT_contra = typing.TypeVar(
    "KeyT_contra",
    bound=typing.Any,
    contravariant=True,
)
ValueT = typing.TypeVar("ValueT", bound=typing.Any)
ValueT_contra = typing.TypeVar(
    "ValueT_contra",
    bound=typing.Any,
    contravariant=True,
)


class RegistryProtocol(typing.Protocol[KeyT_contra, ValueT]):
    """Protocol for registry class."""

    def register(self, for_key: KeyT_contra, item: ValueT): ...

    def register_deco(self, for_key: KeyT_contra): ...

    def remove(self, for_key: KeyT_contra): ...

    def get(self, key: KeyT_contra) -> ValueT | None: ...


class AbstractRegistry(
    RegistryProtocol[KeyT, ValueT],
    typing.Generic[KeyT, ValueT],
    abc.ABC,
):
    """Registry pattern implementation."""

    def __init__(self, raise_on_registered: bool = True) -> None:
        self._raise_on_registered = raise_on_registered

    @abc.abstractmethod
    def _register_item(
        self,
        for_key: KeyT,
        item: ValueT,
    ) -> None:
        """Register item in registry."""

    @abc.abstractmethod
    def _remove_key(
        self,
        for_key: KeyT,
    ) -> None:
        """Remove registered key from registry."""

    @abc.abstractmethod
    def _check_registered(
        self,
        for_key: KeyT,
    ) -> bool:
        """Check if key is already registered."""

    def register(
        self,
        for_key: KeyT,
        item: ValueT,
    ) -> None:
        if self._raise_on_registered and self._check_registered(for_key):
            raise KeyError(f"Key {for_key} is already registered")
        self._register_item(for_key, item)

    def register_deco(
        self,
        for_key: KeyT,
    ) -> collections.abc.Callable[[ValueT], None]:
        def _register(item: ValueT) -> None:
            self.register(for_key, item)

        return _register

    def remove(
        self,
        for_key: KeyT,
        raise_on_missing: bool = False,
    ) -> None:
        if raise_on_missing and not self._check_registered(for_key):
            raise KeyError(f"Key {for_key} is not registered")
        self._remove_key(for_key)


class Registry(AbstractRegistry[KeyT, ValueT]):
    """Default registry implementation."""

    def __init__(self, raise_on_registered: bool = True) -> None:
        super().__init__(raise_on_registered)
        self._registry: dict[KeyT, ValueT] = {}

    def _register_item(
        self,
        for_key: KeyT,
        item: ValueT,
    ) -> None:
        """Register item in registry."""
        self._registry[for_key] = item

    def _remove_key(
        self,
        for_key: KeyT,
    ) -> None:
        """Remove registered key from registry."""
        del self._registry[for_key]

    def _check_registered(
        self,
        for_key: KeyT,
    ) -> bool:
        """Check if key is already registered."""
        return for_key in self._registry

    def get(self, key: KeyT) -> ValueT | None:
        return self._registry.get(key)
