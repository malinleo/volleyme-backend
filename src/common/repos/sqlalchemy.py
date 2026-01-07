import abc
import collections.abc
import typing
import uuid

import sqlalchemy.exc
import sqlalchemy.ext.asyncio
import sqlalchemy.orm.strategy_options

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
    # @abc.abstractmethod
    async def _get_id(instance: models.BaseModel) -> tuple[typing.Any, ...]:
        """Retrieve id from instance."""
        primary_key_fields = instance.__table__.primary_key
        return tuple(getattr(instance, field.name) for field in primary_key_fields)

    # @abc.abstractmethod
    def _build_model_ident_expressions(
        self,
        id: tuple[typing.Any, ...],
        model_class: type[ModelT],
    ) -> collections.abc.Sequence[sqlalchemy.ColumnExpressionArgument[typing.Any]]:
        """Build set of expressions for where clause that identify instance."""
        primary_key_fields = model_class.__table__.primary_key
        return tuple(
            field == id_value for field, id_value in zip(primary_key_fields, id)
        )

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
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
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
        if load_configs:
            query = query.options(*load_configs)
        try:
            return await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.QueryError(
                details=[common_exc.ErrorDetail(message=str(error))],
            ) from error

    async def _try_get_one(
        self,
        id: IdDataT,
        model_class: type[ModelT],
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = set(),
    ) -> ModelT | None:
        """Get one instance by or `None`."""
        result = await self._run_select(
            model_class=model_class,
            where=self._build_model_ident_expressions(
                id=(id,),
                model_class=model_class,
            ),
            load_configs=load_configs,
        )
        return result.unique().scalar_one_or_none()

    async def _get_one(
        self,
        id: IdDataT,
        model_class: type[ModelT],
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = set(),
    ) -> ModelT:
        """Get one instance by or raise error.

        Raises:
            NotFoundError: if object wasn't found.

        """
        if instance := await self._try_get_one(
            id=id,
            model_class=model_class,
            load_configs=load_configs,
        ):
            return instance
        raise exc.NotFoundError(
            details=[common_exc.ErrorDetail(message=f"Object with {id=} wasn't found")],
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
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = set(),
    ) -> collections.abc.Sequence[ModelT]:
        """Get list of instances filtered by `where` conditions."""
        result = await self._run_select(
            model_class=model_class,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
            load_configs=load_configs,
        )
        return result.scalars().unique().all()

    async def _save(
        self,
        instance: ModelT,
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = set(),
    ) -> ModelT:
        """Save instance to db."""
        model_class: type[ModelT] = type(instance)
        self._db_session.add(instance=instance)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise exc.SaveError(
                details=[
                    common_exc.ErrorDetail(message=f"Object save error:\n{error}")
                ],
            ) from error
        instance = (
            await self._get_many(
                model_class=model_class,
                where=self._build_model_ident_expressions(
                    id=await self._get_id(instance=instance),
                    model_class=model_class,
                ),
                order_by=(),
                load_configs=load_configs,
            )
        )[0]
        return instance

    async def _bulk_save(
        self,
        instances: collections.abc.Sequence[ModelT],
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
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
                details=[
                    common_exc.ErrorDetail(message=f"Object save error:\n{error}")
                ],
            ) from error
        where_exprs: list[sqlalchemy.ColumnExpressionArgument[typing.Any]] = []
        for instance in instances:
            exprs = self._build_model_ident_expressions(
                id=await self._get_id(instance=instance),
                model_class=model_class,
            )
            where_exprs.extend(exprs)
        return await self._get_many(
            model_class=model_class,
            where=where_exprs,
            order_by=(),
            load_configs=load_configs,
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
                details=[
                    common_exc.ErrorDetail(message=f"Object save error:\n{error}")
                ],
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
