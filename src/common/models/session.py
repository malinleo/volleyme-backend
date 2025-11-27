import contextlib
import typing
import collections.abc

import sqlalchemy.ext.asyncio

from src.config import settings

async_engine = sqlalchemy.ext.asyncio.create_async_engine(
    url=settings.db_url,
    echo=settings.DEBUG,
)
async_session_factory = sqlalchemy.ext.asyncio.async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)


async def get_db_session() -> collections.abc.AsyncGenerator[
    sqlalchemy.ext.asyncio.AsyncSession, None
]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as ex:
            await session.rollback()
            raise ex
        else:
            await session.commit()


@contextlib.asynccontextmanager
async def get_db_session_context() -> collections.abc.AsyncGenerator[
    sqlalchemy.ext.asyncio.AsyncSession, None
]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as ex:
            await session.rollback()
            raise ex
        else:
            await session.commit()
