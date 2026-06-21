from __future__ import annotations

import datetime
import typing

import sqlalchemy.orm

from src.common.models import base as base_models


class Outbox(base_models.IDModel):
    __tablename__ = "outbox"

    event_type: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(100),
    )
    event_metadata: sqlalchemy.orm.Mapped[dict[str, typing.Any]] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.JSON,
        )
    )
    payload: sqlalchemy.orm.Mapped[dict[str, typing.Any]] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.JSON,
        )
    )
    created_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.text("now()"),
    )
    processing_started_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.DateTime(timezone=True),
            nullable=True,
        )
    )
    sent_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.DateTime(timezone=True),
            nullable=True,
        )
    )
    last_error: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
        nullable=True,
        default=None,
    )
