import typing

from src.volleyme.domain import aggregates, types


class EventInvitationRepo(typing.Protocol):
    """Event repository implementation."""

    async def get_invitation(
        self,
        invitation_id: types.EventInvitationId,
    ) -> aggregates.EventInvitation | None: ...

    async def get_invitations(
        self,
        limit: int,
        offset: int,
    ) -> list[aggregates.EventInvitation]: ...

    async def save_invitation(
        self,
        invitation: aggregates.EventInvitation,
        create: bool = ...,
    ) -> aggregates.EventInvitation: ...

    async def delete_invitation(
        self,
        invitation_id: types.EventInvitationId,
    ) -> None: ...
