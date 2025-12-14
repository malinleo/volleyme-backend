import typing

from src.volleyme.domain import aggregates, types


class UserRepo(typing.Protocol):
    """User repository protocol."""

    async def get_user(self, user_id: types.UserId) -> aggregates.User:
        """Get user by id."""
        ...

    async def get_users(self, limit: int, offset: int) -> list[aggregates.User]:
        """Get list of users with pagination."""
        ...

    async def get_users_by_ids(
        self,
        user_ids: list[types.UserId],
    ) -> list[aggregates.User]:
        """Get list of users by ids."""
        ...

    async def save_user(self, user: aggregates.User) -> aggregates.User:
        """Save user."""
        ...

    async def delete_user(self, user_id: types.UserId) -> None:
        """Delete user by id."""
        ...
