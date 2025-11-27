import typing
from src.volleyme.domain import types, aggregates


class PlayerRepo(typing.Protocol):
    """Player repository protocol."""

    async def get_player(self, player_id: types.PlayerId) -> aggregates.Player:
        """Get player by id."""
        ...

    async def get_players(self, limit: int, offset: int) -> list[aggregates.Player]:
        """Get list of players with pagination."""
        ...

    async def save_player(self, player: aggregates.Player) -> aggregates.Player:
        """Save player."""
        ...

    async def delete_player(self, player_id: types.PlayerId) -> None:
        """Delete player by id."""
        ...
