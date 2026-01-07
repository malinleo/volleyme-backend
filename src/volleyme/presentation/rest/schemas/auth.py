import pydantic

from src.common import schemas
from src.volleyme.presentation import auth
from src.config import settings


class EmailPasswordLoginRequest(schemas.BaseSchema):
    email: str = pydantic.Field(max_length=255)
    password: str = pydantic.Field(max_length=settings.PASSWORD_MAX_LENGTH)


class EmailPasswordRegisterRequest(schemas.BaseSchema):
    email: str = pydantic.Field(max_length=255)
    password: str = pydantic.Field(max_length=settings.PASSWORD_MAX_LENGTH)


class JWTAuthTokenResponse(schemas.BaseSchema):
    token_type: auth.AuthTokenSchema
    access_token: str
