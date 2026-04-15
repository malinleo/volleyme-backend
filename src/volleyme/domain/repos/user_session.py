import typing

from src.volleyme.domain import aggregates, types


class UserSessionRepo(typing.Protocol):
    """User repository protocol."""

    async def get_session(
        self,
        session_id: types.UserSessionId,
    ) -> aggregates.UserSession | None:
        """Get session by id."""
        ...

    async def get_user_sessions(
        self,
        user_id: types.UserId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[aggregates.UserSession]:
        """Get all user sessions by user id."""
        ...

    async def save_session(
        self,
        session: aggregates.UserSession,
        create: bool = ...,
    ) -> aggregates.UserSession:
        """Save session."""
        ...

    async def delete_session(self, session_id: types.UserSessionId) -> None:
        """Delete session by id."""
        ...
