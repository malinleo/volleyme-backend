import pydantic

from src.common import schemas
from src.volleyme.presentation import auth


class EmailPasswordLoginRequest(schemas.BaseSchema):
    email: str = pydantic.Field(max_length=255)
    password: str = pydantic.Field(max_length=255)


class JWTAuthTokenResponse(schemas.BaseSchema):
    token_type: auth.AuthTokenSchema
    access_token: str
