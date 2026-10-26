import dataclasses

from src.common import usecases
from src.volleyme.application import dto, services


@dataclasses.dataclass(frozen=True)
class HealthCheckUseCase(usecases.BaseUseCase):
    health_service: services.health.HealthService

    async def execute(self) -> dto.HealthCheckDto:
        return await self.health_service.perform_health_check()
