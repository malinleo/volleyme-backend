import sqlalchemy.exc
import sqlalchemy.orm

from src.common import exc as common_exc
from src.common import repos as common_repos
from src.volleyme.application import dto, query_repos
from src.volleyme.domain import aggregates, enums, repos, types
from src.volleyme.infra.db import models


class EventRepo(
    common_repos.SQLAlchemyIdModelRepo,
    repos.EventRepo,
):
    """Event repository implementation."""

    _model_class = models.Event

    def _parse_event_model(self, event_model: models.Event) -> aggregates.Event:
        event = aggregates.Event(
            id=types.EventId(event_model.id),
            start_dt=event_model.start_dt,
            end_dt=event_model.end_dt,
            title=event_model.title,
            game_type=event_model.game_type,
            format_type=event_model.format_type,
            country=event_model.country,
            city=event_model.city,
            address=event_model.address,
            max_participants_count=event_model.max_participants_count,
            participants={
                types.UserId(participant.id) for participant in event_model.participants
            },
            hosts={types.UserId(host.id) for host in event_model.hosts},
            description=event_model.description,
            price=event_model.price,
            currency=event_model.currency,
            image_urls=event_model.image_urls,
            games=[],
            created_by=types.UserId(event_model.created_by_id),
            updated_by=types.UserId(event_model.updated_by_id),
        )
        for game_model in event_model.games:
            game = aggregates.Game(
                event=event,
                type=game_model.type,
                type_info=game_model.type_info,
                teams=[],
            )
            for team_model in game_model.teams:
                team = aggregates.GameTeam(
                    game=game,
                    title=team_model.title,
                    score=team_model.score,
                    players=[
                        types.PlayerId(player_id) for player_id in team_model.players
                    ],
                )
                game.teams.append(team)
            event.games.append(game)
        return event

    async def get_event(self, event_id: types.EventId) -> aggregates.Event | None:
        event_model = await self._try_get_one(
            model_class=self._model_class,
            id=event_id,
            load_configs={
                sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                    models.Game.teams,
                ),
                sqlalchemy.orm.joinedload(self._model_class.participants),
                sqlalchemy.orm.joinedload(self._model_class.hosts),
            },
        )
        if event_model:
            return self._parse_event_model(event_model)
        return None

    async def get_events(self, limit: int, offset: int) -> list[aggregates.Event]:
        event_models = await self._get_many(
            model_class=self._model_class,
            where=(),
            order_by=(),
            limit=limit,
            offset=offset,
            load_configs={
                sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                    models.Game.teams,
                ),
                sqlalchemy.orm.joinedload(self._model_class.participants),
                sqlalchemy.orm.joinedload(self._model_class.hosts),
            },
        )
        return [self._parse_event_model(event_model) for event_model in event_models]

    async def save_event(
        self,
        event: aggregates.Event,
        create: bool = False,
    ) -> aggregates.Event:
        event_model = models.Event(
            id=event.id,
            start_dt=event.start_dt,
            end_dt=event.end_dt,
            title=event.title,
            game_type=event.game_type,
            format_type=event.format_type,
            country=event.country,
            city=event.city,
            address=event.address,
            max_participants_count=event.max_participants_count,
            description=event.description,
            price=event.price,
            currency=event.currency,
            image_urls=event.image_urls,
            created_at=event.created_at,
            updated_at=event.updated_at,
            created_by_id=event.created_by,
            updated_by_id=event.updated_by,
        )
        saved_event = self._parse_event_model(
            await self._save(
                event_model,
                create=create,
                load_configs={
                    sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                        models.Game.teams,
                    ),
                    sqlalchemy.orm.joinedload(self._model_class.participants),
                    sqlalchemy.orm.joinedload(self._model_class.hosts),
                },
            )
        )
        participants_rels = [
            models.EventParticipantRel(event_id=event_model.id, user_id=participant)
            for participant in event.participants
        ]
        hosts_rels = [
            models.EventHostRel(event_id=event_model.id, user_id=host)
            for host in event.hosts
        ]
        await self._bulk_save(participants_rels, create=create)
        await self._bulk_save(hosts_rels, create=create)
        return saved_event

    async def delete_event(self, event_id: types.EventId) -> None:
        return await self._delete(
            model_class=self._model_class,
            where=self._build_model_ident_expressions(
                id=(event_id,),
                model_class=self._model_class,
            ),
        )


class EventQueryRepo(
    common_repos.SQLAlchemyIdModelRepo,
    query_repos.EventQueryRepo,
):
    """Event query repository implementation."""

    _model_class = models.Event

    async def get_event_info_for_user(
        self,
        event_id: types.EventId,
        user_id: types.UserId,
    ) -> dto.EventDetailsDto | None:
        query = (
            sqlalchemy.select(self._model_class)
            .join(
                models.EventParticipantRel,
                onclause=self._model_class.id == models.EventParticipantRel.event_id,
                isouter=True,
            )
            .group_by(self._model_class.id)
            .where(self._model_class.id == event_id)
            .options(
                sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                    models.Game.teams,
                ),
                sqlalchemy.orm.joinedload(self._model_class.participants).selectinload(
                    models.User.profile,
                ),
                sqlalchemy.orm.joinedload(self._model_class.hosts).selectinload(
                    models.User.profile,
                ),
                sqlalchemy.orm.with_expression(
                    self._model_class.participants_count,
                    sqlalchemy.func.count(models.EventParticipantRel.event_id),
                ),
                sqlalchemy.orm.with_expression(
                    self._model_class.my_role,
                    sqlalchemy.case(
                        (
                            self._model_class.hosts.any(models.User.id == user_id),
                            enums.EventParticipantRole.HOST.value,
                        ),
                        (
                            self._model_class.participants.any(
                                models.User.id == user_id
                            ),
                            enums.EventParticipantRole.PARTICIPANT.value,
                        ),
                        else_=enums.EventParticipantRole.NOBODY.value,
                    ),
                ),
            )
        )
        try:
            result = await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise common_repos.exc.QueryError(
                details=[common_exc.ErrorDetail(message=str(error))],
            ) from error
        event_model = result.unique().scalar_one_or_none()
        if event_model:
            return dto.EventDetailsDto(
                id=event_model.id,
                title=event_model.title,
                start_dt=event_model.start_dt,
                end_dt=event_model.end_dt,
                city=event_model.city,
                address=event_model.address,
                participants_count=event_model.participants_count,
                max_participants_count=event_model.max_participants_count,
                my_role=event_model.my_role,
                price=event_model.price,
                currency=event_model.currency,
                description=event_model.description,
                image_urls=event_model.image_urls,
                country=event_model.country,
                game_type=event_model.game_type,
                format_type=event_model.format_type,
                participants=[
                    dto.ParticipantInfoDto(
                        id=participant.id,
                        avatar_url=(
                            participant.profile.avatar_url
                            if participant.profile
                            else None
                        ),
                        name=(
                            participant.profile.full_name
                            if participant.profile
                            else None
                        ),
                    )
                    for participant in event_model.participants
                ],
                hosts=[
                    dto.ParticipantInfoDto(
                        id=host.id,
                        avatar_url=host.profile.avatar_url if host.profile else None,
                        name=host.profile.full_name if host.profile else None,
                    )
                    for host in event_model.hosts
                ],
            )
        return None

    async def get_events_info_for_user(
        self,
        user_id: types.UserId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dto.EventListDto]:
        query = (
            sqlalchemy.select(self._model_class)
            .join_from(
                self._model_class,
                models.EventParticipantRel,
                onclause=self._model_class.id == models.EventParticipantRel.event_id,
            )
            .group_by(self._model_class.id)
            .limit(limit)
            .offset(offset)
            .options(
                sqlalchemy.orm.joinedload(self._model_class.games).joinedload(
                    models.Game.teams,
                ),
                sqlalchemy.orm.joinedload(self._model_class.participants),
                sqlalchemy.orm.joinedload(self._model_class.hosts),
                sqlalchemy.orm.with_expression(
                    self._model_class.participants_count,
                    sqlalchemy.func.count(models.EventParticipantRel.event_id),
                ),
                sqlalchemy.orm.with_expression(
                    self._model_class.my_role,
                    sqlalchemy.case(
                        (
                            self._model_class.hosts.any(models.User.id == user_id),
                            enums.EventParticipantRole.HOST.value,
                        ),
                        (
                            self._model_class.participants.any(
                                models.User.id == user_id
                            ),
                            enums.EventParticipantRole.PARTICIPANT.value,
                        ),
                        else_=enums.EventParticipantRole.NOBODY.value,
                    ),
                ),
            )
        )
        try:
            result = await self._db_session.execute(query)
        except sqlalchemy.exc.SQLAlchemyError as error:
            raise common_repos.exc.QueryError(
                details=[common_exc.ErrorDetail(message=str(error))],
            ) from error
        event_models_list = result.unique().scalars().all()
        return [
            dto.EventListDto(
                id=event_model.id,
                title=event_model.title,
                start_dt=event_model.start_dt,
                city=event_model.city,
                address=event_model.address,
                price=event_model.price,
                participants_count=event_model.participants_count,
                my_role=event_model.my_role,
                image_urls=event_model.image_urls,
                country=event_model.country,
                currency=event_model.currency,
                game_type=event_model.game_type,
            )
            for event_model in event_models_list
        ]
