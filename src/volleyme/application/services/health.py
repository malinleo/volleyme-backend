import typing

from src.volleyme.application import dto


class HealthService(typing.Protocol):
    async def perform_health_check(self) -> dto.HealthCheckDto: ...
