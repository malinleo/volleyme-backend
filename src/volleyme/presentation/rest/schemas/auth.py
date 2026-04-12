import pydantic

from src.common import schemas
from src.config import settings
from src.volleyme.presentation import auth


class LoginRequest(schemas.BaseSchema):
    username: str = pydantic.Field(max_length=255)
    password: str = pydantic.Field(max_length=settings.PASSWORD_MAX_LENGTH)


class RegisterRequest(schemas.BaseSchema):
    username: str = pydantic.Field(max_length=255)
    first_name: str | None = pydantic.Field(max_length=255, default=None)
    last_name: str | None = pydantic.Field(max_length=255, default=None)
    avatar_url: str | None = pydantic.Field(default=None)
    password: str = pydantic.Field(max_length=settings.PASSWORD_MAX_LENGTH)


class JWTAuthTokenResponse(schemas.BaseSchema):
    token_type: auth.AuthTokenSchema
    access_token: str
