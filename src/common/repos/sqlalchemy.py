import abc
import asyncio
import collections.abc
import typing

import sqlalchemy.exc
import sqlalchemy.ext.asyncio
import sqlalchemy.orm
import uuid
from src.common import exc as common_exc
from src.common import models

from . import exc

ModelT = typing.TypeVar("ModelT", bound=models.BaseModel)
IdDataT = typing.TypeVar("IdDataT")


class SQLAlchemyModelRepo(
    typing.Generic[IdDataT],
    abc.ABC,
):
    """Base repo logic for sqlalchemy."""

    def __init__(self, db_session: sqlalchemy.ext.asyncio.AsyncSession) -> None:
        self._db_session = db_session

    @staticmethod
    @abc.abstractmethod
    async def _get_id(instance: models.BaseModel) -> IdDataT:
        """Retrieve id from instance."""

    @abc.abstractmethod
    def _build_model_ident_expressions(
        self,
        id: IdDataT,
        model_class: type[ModelT],
    ) -> collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[typing.Any]]:
        """Build set of expressions for where clause that identify instance."""

    async def _run_select(
        self,
        model_class: type[ModelT],
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
        ] = set(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
    ) -> sqlalchemy.Result[tuple[ModelT, ...]]:
        """Get result of select query."""
        query = (
            sqlalchemy.select(model_class)
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
        model_class: type[ModelT],
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
    ) -> ModelT | None:
        """Get one instance by or `None`."""
        result = await self._run_select(
            model_class=model_class,
            where=self._build_model_ident_expressions(id=id, model_class=model_class),
            selectin_load_fields=selectin_load_fields,
            joined_load_fields=joined_load_fields,
        )
        return result.scalar_one_or_none()

    async def _get_one(
        self,
        id: IdDataT,
        model_class: type[ModelT],
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
    ) -> ModelT:
        """Get one instance by or raise error.

        Raises:
            NotFoundError: if object wasn't found.

        """
        if instance := await self._try_get_one(
            id=id,
            model_class=model_class,
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
        model_class: type[ModelT],
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
        ] = set(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
    ) -> collections.abc.Sequence[ModelT]:
        """Get list of instances filtered by `where` conditions."""
        result = await self._run_select(
            model_class=model_class,
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
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
    ) -> ModelT:
        """Save instance to db."""
        model_class: type[ModelT] = type(instance)
        self._db_session.add(instance=instance)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                msg=f"{common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_SAVE]}"
                f":\n{error}",
            ) from error
        instance = (
            await self._get_many(
                model_class=model_class,
                where=self._build_model_ident_expressions(
                    id=await self._get_id(instance=instance),
                    model_class=model_class,
                ),
                order_by=(),
                selectin_load_fields=selectin_load_fields,
                joined_load_fields=joined_load_fields,
            )
        )[0]
        return instance

    async def _bulk_save(
        self,
        instances: collections.abc.Sequence[ModelT],
        selectin_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
        joined_load_fields: collections.abc.Set[
            sqlalchemy.orm.InstrumentedAttribute[typing.Any],
        ] = set(),
    ) -> collections.abc.Sequence[ModelT]:
        """Save multiple instances."""
        if not instances:
            return instances
        model_class: type[ModelT] = type(instances[0])
        self._db_session.add_all(instances=instances)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                msg=f"{common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_SAVE]}",
            ) from error
        where_exprs = (
            self._build_model_ident_expressions(
                id=await self._get_id(instance=instance),
                model_class=model_class,
            )
            for instance in instances
        )
        return await self._get_many(
            model_class=model_class,
            where=tuple(*sqlalchemy.and_(*where_exprs)),
            order_by=(),
            selectin_load_fields=selectin_load_fields,
            joined_load_fields=joined_load_fields,
        )

    async def _delete(
        self,
        model_class: type[ModelT],
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ],
    ) -> None:
        """Delete objects from table by condition."""
        query = sqlalchemy.delete(model_class).where(*where)
        try:
            await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                msg=f"{common_exc.ERROR_TEXTS[common_exc.ErrorCode.REPO_SAVE]}",
            ) from error

    async def _delete_instance(
        self, model_class: type[ModelT], instance: ModelT
    ) -> None:
        """Delete objects from table by condition."""
        return await self._delete(
            model_class=model_class,
            where=self._build_model_ident_expressions(
                id=await self._get_id(instance=instance),
                model_class=model_class,
            ),
        )


IdModelT = typing.TypeVar("IdModelT", bound=models.IDModel)


class SQLAlchemyIdModelRepo(SQLAlchemyModelRepo[uuid.UUID]):
    """Base repo class for default id models."""

    @staticmethod
    async def _get_id(instance: models.IDModel) -> uuid.UUID:
        return instance.id

    def _build_model_ident_expressions(
        self,
        id: uuid.UUID,
        model_class: type[models.IDModel],
    ) -> collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[typing.Any]]:
        return (model_class.id == id,)
