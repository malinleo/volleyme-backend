from src.common import dto


class ServiceCheckResultDto(dto.BaseDto):
    is_healthy: bool
    error: str | None = None

    def __bool__(self) -> bool:
        return self.is_healthy


class HealthCheckDto(dto.BaseDto):
    is_healthy: bool
    db: ServiceCheckResultDto
    rabbit: ServiceCheckResultDto
