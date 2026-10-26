from src.common import schemas


class ServiceCheckResult(schemas.BaseSchema):
    is_healthy: bool
    error: str | None = None


class HealthCheckResponse(schemas.BaseSchema):
    is_healthy: bool
    db: ServiceCheckResult
    rabbit: ServiceCheckResult
