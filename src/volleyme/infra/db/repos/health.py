import sqlalchemy

from src.volleyme.application import dto

from . import base


class HealthCheckQueryRepo(base.SQLAlchemyModelRepo):
    """Health check query repository implementation."""

    async def perform_health_check(self) -> dto.ServiceCheckResultDto:
        """Perform health check."""
        try:
            await self._try_execute(query=sqlalchemy.select(1))
        except Exception as e:
            return dto.ServiceCheckResultDto(is_healthy=False, error=str(e))
        return dto.ServiceCheckResultDto(is_healthy=True)
