import sqlalchemy.ext.asyncio
from dependency_injector import containers, providers

from src.common import models as common_models
from src.config import settings
from src.volleyme.infra.db import repos


class Infra(containers.DeclarativeContainer):
    async_engine = providers.Singleton(
        sqlalchemy.ext.asyncio.create_async_engine,
        url=settings.db_url,
        echo=settings.DEBUG,
    )
    async_session_factory = providers.Resource(
        sqlalchemy.ext.asyncio.async_sessionmaker,
        async_engine,
        expire_on_commit=False,
    )
    db_session = providers.Resource(
        common_models.get_db_session,
        async_session_factory=async_session_factory,
    )
    event_repo = providers.Factory(
        repos.EventRepo,
        db_session=db_session,
    )
