import asyncio
import dataclasses

import aio_pika

from src.volleyme.application import dto, services
from src.volleyme.infra.db.repos import health as health_repos


@dataclasses.dataclass(frozen=True, kw_only=True)
class HealthService(services.health.HealthService):
    amqp_url: str
    health_check_query_repo: health_repos.HealthCheckQueryRepo

    async def perform_health_check(self) -> dto.HealthCheckDto:
        db_health = await self.health_check_query_repo.perform_health_check()
        rabbit_health = await self._check_rabbit()
        is_healthy = all((db_health, rabbit_health))
        return dto.HealthCheckDto(
            is_healthy=is_healthy,
            db=db_health,
            rabbit=rabbit_health,
        )

    async def _check_rabbit(self):
        try:
            await asyncio.wait_for(
                aio_pika.connect_robust(self.amqp_url),
                timeout=5.0,
            )
        except Exception as e:
            rabbit_health = dto.ServiceCheckResultDto(is_healthy=False, error=str(e))
        else:
            rabbit_health = dto.ServiceCheckResultDto(is_healthy=True)
        return rabbit_health
