import abc
import collections.abc
import typing
import uuid

import sqlalchemy.exc
import sqlalchemy.ext.asyncio
import sqlalchemy.orm.strategy_options
import sqlalchemy.sql.selectable

from src.common import exc as common_exc
from src.common import models
from src.volleyme.domain import repos

ModelT = typing.TypeVar("ModelT", bound=models.BaseModel)
RelatedModelT = typing.TypeVar("RelatedModelT", bound=models.BaseModel)
IdDataT = typing.TypeVar("IdDataT", bound=tuple[typing.Any, ...])


ResultT = typing.TypeVar("ResultT")


class QueryResult(typing.NamedTuple, typing.Generic[ResultT]):
    result: sqlalchemy.Result[tuple[ResultT]]
    query_str: str


class SQLAlchemyModelRepo(
    typing.Generic[IdDataT],
    abc.ABC,
):
    """Base repo logic for sqlalchemy."""

    def __init__(self, db_session: sqlalchemy.ext.asyncio.AsyncSession) -> None:
        self._db_session = db_session

    @staticmethod
    def _get_id(instance: models.BaseModel) -> tuple[typing.Any, ...]:
        """Retrieve id from instance."""
        primary_key_fields = instance.__table__.primary_key
        return tuple(getattr(instance, field.name) for field in primary_key_fields)

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
        ] = frozenset(),
    ) -> QueryResult[ModelT]:
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
        return await self._try_execute(query=query)

    @typing.overload
    async def _try_execute(
        self,
        query: sqlalchemy.Select[tuple[ResultT]],
    ) -> QueryResult[ResultT]: ...

    @typing.overload
    async def _try_execute(
        self,
        query: sqlalchemy.Delete,
    ) -> QueryResult[typing.Any]: ...

    async def _try_execute(
        self,
        query: sqlalchemy.Select[tuple[ResultT]] | sqlalchemy.Delete,
    ) -> QueryResult[ResultT]:
        query_str = str(
            query.compile(
                compile_kwargs={"literal_binds": True},
                dialect=self._db_session.bind.dialect,
            ).statement
        )
        try:
            return QueryResult(
                result=await self._db_session.execute(query),
                query_str=query_str,
            )
        except sqlalchemy.exc.DBAPIError as error:
            await self._db_session.rollback()
            raise repos.exc.QueryError(
                query=error.statement or "Unknown query"
            ) from error
        except sqlalchemy.exc.SQLAlchemyError as error:
            await self._db_session.rollback()
            raise repos.exc.RepoError(
                details=[
                    common_exc.ErrorDetail(
                        code=repos.exc.ErrorCode.REPO,
                        messages=[f"Sqlalchemy error: {error}"],
                    )
                ],
            ) from error

    async def _try_get_one(
        self,
        id: IdDataT,
        model_class: type[ModelT],
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ] = tuple(),
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = frozenset(),
    ) -> tuple[ModelT | None, str]:
        """Get one instance or `None`."""
        where_exprs: list[sqlalchemy.ColumnExpressionArgument[typing.Any]] = [
            *self._build_model_ident_expressions(
                id=id,
                model_class=model_class,
            ),
            *where,
        ]
        result = await self._run_select(
            model_class=model_class,
            where=where_exprs,
            load_configs=load_configs,
        )
        return result.result.unique().scalar_one_or_none(), result.query_str

    async def _get_one(
        self,
        id: IdDataT,
        model_class: type[ModelT],
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ] = tuple(),
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = set(),
    ) -> ModelT:
        """Get one instance by or raise error.

        Raises:
            NotFoundError: if object wasn't found.

        """
        instance, query_str = await self._try_get_one(
            id=id,
            model_class=model_class,
            where=where,
            load_configs=load_configs,
        )
        if instance:
            return instance
        raise repos.exc.NotFoundError(query=query_str)

    async def _get_many(
        self,
        model_class: type[ModelT],
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ],
        order_by: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ] = tuple(),
        limit: int | None = None,
        offset: int | None = None,
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = set(),
    ) -> tuple[collections.abc.Sequence[ModelT], str]:
        """Get list of instances filtered by `where` conditions."""
        result = await self._run_select(
            model_class=model_class,
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
            load_configs=load_configs,
        )
        return result.result.scalars().unique().all(), result.query_str

    async def _save(
        self,
        instance: ModelT,
        create: bool = False,
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = frozenset(),
    ) -> ModelT:
        """Save instance to db."""
        model_class: type[ModelT] = type(instance)
        if create:
            self._db_session.add(instance=instance)
        else:
            await self._db_session.merge(instance=instance)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.DBAPIError as error:
            await self._db_session.rollback()
            raise repos.exc.SaveError(
                query=error.statement or "Unknown query",
            ) from error
        except sqlalchemy.exc.SQLAlchemyError as error:
            await self._db_session.rollback()
            raise repos.exc.RepoError(
                details=[
                    common_exc.ErrorDetail(
                        code=repos.exc.ErrorCode.REPO,
                        messages=[f"Sqlalchemy error: {error}"],
                    )
                ],
            ) from error
        result = await self._get_many(
            model_class=model_class,
            where=self._build_model_ident_expressions(
                id=self._get_id(instance=instance),
                model_class=model_class,
            ),
            order_by=(),
            load_configs=load_configs,
        )
        return result[0][0]

    async def _bulk_save(
        self,
        instances: collections.abc.Sequence[ModelT],
        create: bool = False,
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = frozenset(),
    ) -> collections.abc.Sequence[ModelT]:
        """Save multiple instances."""
        if not instances:
            return instances
        model_class: type[ModelT] = type(instances[0])
        if create:
            self._db_session.add_all(instances=instances)
        else:
            for instance in instances:
                await self._db_session.merge(instance=instance)
        try:
            await self._db_session.flush()
        except sqlalchemy.exc.DBAPIError as error:
            await self._db_session.rollback()
            raise repos.exc.SaveError(
                query=error.statement or "Unknown query",
            ) from error
        except sqlalchemy.exc.SQLAlchemyError as error:
            await self._db_session.rollback()
            raise repos.exc.RepoError(
                details=[
                    common_exc.ErrorDetail(
                        code=repos.exc.ErrorCode.REPO,
                        messages=[f"Sqlalchemy error: {error}"],
                    )
                ],
            ) from error
        where_exprs: list[sqlalchemy.ColumnExpressionArgument[typing.Any]] = []
        for instance in instances:
            exprs = self._build_model_ident_expressions(
                id=self._get_id(instance=instance),
                model_class=model_class,
            )
            where_exprs.extend(exprs)
        result = await self._get_many(
            model_class=model_class,
            where=where_exprs,
            order_by=(),
            load_configs=load_configs,
        )
        return result[0]

    async def _delete(
        self,
        model_class: type[ModelT],
        where: collections.abc.Sequence[
            sqlalchemy.ColumnExpressionArgument[typing.Any]
        ],
    ) -> None:
        """Delete objects from table by condition."""
        query = sqlalchemy.delete(model_class).where(*where)
        await self._try_execute(query=query)

    async def _delete_instance(
        self,
        instance: models.BaseModel,
    ) -> None:
        """Delete instance from database."""
        model_class: type[models.BaseModel] = type(instance)
        return await self._delete(
            model_class=model_class,
            where=self._build_model_ident_expressions(
                id=self._get_id(instance=instance),
                model_class=model_class,
            ),
        )

    async def _delete_instances(
        self,
        instances: collections.abc.Sequence[models.BaseModel],
    ) -> None:
        """Delete instances from database."""
        if not instances:
            return
        model_class: type[models.BaseModel] = type(instances[0])
        where_exprs: list[sqlalchemy.ColumnExpressionArgument[typing.Any]] = []
        for instance in instances:
            exprs = self._build_model_ident_expressions(
                id=self._get_id(instance=instance),
                model_class=model_class,
            )
            where_exprs.extend(exprs)
        await self._delete(model_class=model_class, where=where_exprs)

    async def _save_relations(
        self,
        existing_instances: collections.abc.Sequence[ModelT],
        new_instances: collections.abc.Sequence[ModelT],
        get_rel_id: collections.abc.Callable[[ModelT], tuple[typing.Any, ...]],
        load_configs: collections.abc.Set[
            sqlalchemy.orm.strategy_options._AbstractLoad
        ] = frozenset(),
    ) -> tuple[collections.abc.Sequence[ModelT], collections.abc.Sequence[ModelT]]:
        """Save relations between instances."""
        old_instances_ids = {get_rel_id(instance) for instance in existing_instances}
        new_instances_ids = {get_rel_id(instance) for instance in new_instances}
        removed_instances_ids = old_instances_ids - new_instances_ids
        added_instances_ids = new_instances_ids - old_instances_ids
        removed_rels = [
            instance
            for instance in existing_instances
            if get_rel_id(instance) in removed_instances_ids
        ]
        added_rels = [
            instance
            for instance in new_instances
            if get_rel_id(instance) in added_instances_ids
        ]
        await self._bulk_save(added_rels, create=True, load_configs=load_configs)
        await self._delete_instances(removed_rels)
        return added_rels, removed_rels


IdModelT = typing.TypeVar("IdModelT", bound=models.IDModel)


class SQLAlchemyIdModelRepo(SQLAlchemyModelRepo[tuple[uuid.UUID]]):
    """Base repo class for default id models."""
