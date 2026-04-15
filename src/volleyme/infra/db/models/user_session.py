from __future__ import annotations

import datetime
import typing
import uuid

import sqlalchemy.orm

from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .user import User


class UserSession(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "user_session"
    __table_args__ = (sqlalchemy.Index("idx_user_session_user_id", "user_id"),)

    user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("user.id", name="fk_user_session_user_id"),
    )
    user: sqlalchemy.orm.Mapped[User] = sqlalchemy.orm.relationship(
        "User",
        back_populates="sessions",
        foreign_keys=[user_id],
        lazy="raise",
    )
    expires_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
    )
    revoked_at: sqlalchemy.orm.Mapped[datetime.datetime | None] = (
        sqlalchemy.orm.mapped_column(
            sqlalchemy.DateTime(timezone=True),
            nullable=True,
        )
    )
