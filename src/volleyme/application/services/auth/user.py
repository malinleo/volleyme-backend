import dataclasses

from src.volleyme.domain import types


@dataclasses.dataclass
class AuthUser:
    id: types.UserId
