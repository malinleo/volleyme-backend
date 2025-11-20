import abc
import asyncio
import collections.abc
import typing

import sqlalchemy.exc
import sqlalchemy.ext.asyncio
import sqlalchemy.orm

from src.common import exc as common_exc
from src.common import models

from . import exc

ModelT = typing.TypeVar("ModelT", bound=models.BaseModel)
IdDataT = typing.TypeVar("IdDataT")


class SQLAlchemyModelRepo(
    typing.Generic[ModelT, IdDataT],
    abc.ABC,
):
    """Base repo logic for sqlalchemy."""

    _model_class: type[ModelT]
    _default_selectin_load_fields: frozenset[
        sqlalchemy.orm.InstrumentedAttribute[typing.Any]
    ]
    _default_joined_load_fields: frozenset[
        sqlalchemy.orm.InstrumentedAttribute[typing.Any]
    ]

    def __init__(self, db_session: sqlalchemy.ext.asyncio.AsyncSession) -> None:
        self._db_session = db_session

    @staticmethod
    @abc.abstractmethod
    async def _get_id(instance: ModelT) -> IdDataT:
        """Retrieve id from instance."""

    @abc.abstractmethod
    def _build_model_ident_expressions(
        self,
        id: IdDataT,
    ) -> collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[typing.Any]]:
        """Build set of expressions for where clause that identify instance."""

    async def _run_select(
        self,
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ] = tuple(),
        order_by: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ] = tuple(),
        limit: int | None = None,
        offset: int | None = None,
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
    ) -> sqlalchemy.Result[tuple[ModelT, ...]]:
        """Get result of select query."""
        query = (
            sqlalchemy.select(self._model_class)
            .where(*where)
            .order_by(*order_by)
            .limit(limit=limit)
            .offset(offset=offset)
        )
        if selectin_load_fields:
            query = query.options(
                sqlalchemy.orm.selectinload(*selectin_load_fields),
            )
        if joined_load_fields:
            query = query.options(
                sqlalchemy.orm.joinedload(*joined_load_fields),
            )
        try:
            return await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.QueryError from error

    async def _try_get_one(
        self,
        id: IdDataT,
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
    ) -> ModelT | None:
        """Get one instance by or `None`."""
        result = await self._run_select(
            where=self._build_model_ident_expressions(id=id),
            selectin_load_fields=selectin_load_fields,
            joined_load_fields=joined_load_fields,
        )
        return result.scalar_one_or_none()

    async def _get_one(
        self,
        id: IdDataT,
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
    ) -> ModelT:
        """Get one instance by or raise error.

        Raises:
            NotFoundError: if object wasn't found.

        """
        if instance := await self._try_get_one(
            id=id,
            selectin_load_fields=selectin_load_fields,
            joined_load_fields=joined_load_fields,
        ):
            return instance
        raise exc.NotFoundError(
            msg=common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_NOT_FOUND].format(
                object_data=f"id = {id}",
            ),
        )

    async def _get_many(
        self,
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ],
        order_by: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ],
        limit: int | None = None,
        offset: int | None = None,
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = frozenset(),
    ) -> collections.abc.Sequence[ModelT]:
        """Get list of instances filtered by `where` conditions."""
        result = await self._run_select(
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
            selectin_load_fields=selectin_load_fields,
            joined_load_fields=joined_load_fields,
        )
        return result.scalars().unique().all()

    async def _save(
        self,
        instance: ModelT,
        with_refresh: bool = True,
    ) -> ModelT:
        """Save instance to db."""
        self._db_session.add(instance=instance)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                msg=f"{common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_SAVE]}"
                f":\n{error}",
            ) from error
        if with_refresh:
            await self._db_session.refresh(instance=instance)
        return instance

    async def _bulk_save(
        self,
        instances: collections.abc.Sequence[ModelT],
        with_refresh: bool = True,
    ) -> collections.abc.Sequence[ModelT]:
        """Save multiple instances."""
        self._db_session.add_all(instances=instances)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                msg=f"{common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_SAVE]}",
            ) from error
        if with_refresh:
            await asyncio.gather(
                *(self._db_session.refresh(instance=instance) for instance in instances)
            )
        return instances

    async def _delete(
        self,
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ],
    ) -> None:
        """Delete objects from table by condition."""
        query = sqlalchemy.delete(self._model_class).where(*where)
        try:
            await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                msg=f"{common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_SAVE]}",
            ) from error

    async def _delete_instance(self, instance: ModelT) -> None:
        """Delete objects from table by condition."""
        return await self._delete(
            where=self._build_model_ident_expressions(
                id=await self._get_id(instance=instance),
            ),
        )


IdModelT = typing.TypeVar("IdModelT", bound=models.IDModel)


class SQLAlchemyIdModelRepo(SQLAlchemyModelRepo[IdModelT, int]):
    """Base repo class for default id models."""

    @staticmethod
    async def _get_id(instance: IdModelT) -> int:
        return instance.id

    def _build_model_ident_expressions(
        self,
        id: int,
    ) -> collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[typing.Any]]:
        return (self._model_class.id == id,)
