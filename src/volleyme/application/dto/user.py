from src.common import dto
from src.volleyme.domain import types


class UserAuthDto(dto.BaseDto):
    id: types.UserId
    email: str
    password: str
