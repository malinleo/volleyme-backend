import typing

from src.volleyme.application import dto


class HealthCheckQueryRepo(typing.Protocol):
    """Health check repository protocol."""

    async def perform_health_check(self) -> dto.ServiceCheckResultDto:
        """Perform health check."""
        ...
