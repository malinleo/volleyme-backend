import dataclasses

from src.common import usecases
from src.volleyme.application import dto, query_repos


@dataclasses.dataclass(frozen=True)
class HealthCheckUseCase(usecases.BaseUseCase):
    health_check_query_repo: query_repos.HealthCheckQueryRepo

    async def execute(self) -> dto.HealthCheckDto:
        db_health = await self.health_check_query_repo.perform_health_check()
        is_healthy = all((db_health,))
        return dto.HealthCheckDto(is_healthy=is_healthy, db=db_health)
