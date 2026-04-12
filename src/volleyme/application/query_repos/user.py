import typing

from src.volleyme.application import dto


class UserQueryRepo(typing.Protocol):
    """User query repository protocol."""

    async def get_user_auth_info(self, username: str) -> dto.UserAuthDto | None:
        """Get user auth info by username."""
        ...
