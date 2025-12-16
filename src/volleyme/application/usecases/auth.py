import dataclasses

from src.common import usecases
from src.volleyme.application import services


@dataclasses.dataclass
class AuthUseCase:
    auth_strategy: services.AuthStrategy

    async def execute(self) -> services.AuthUser:
        try:
            auth_user = await self.auth_strategy.authenticate()
        except services.AuthError as auth_error:
            raise usecases.exc.UseCaseError(
                msg=auth_error.msg,
                code=auth_error.code,
            )
        if not auth_user:
            raise usecases.exc.UseCaseError(
                msg="User with given credentials wasn't found"
            )
        return auth_user
