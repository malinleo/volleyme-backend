from __future__ import annotations

import typing
import uuid

import sqlalchemy.orm

from src.common.models import base as base_models

if typing.TYPE_CHECKING:
    from .user import User


class Profile(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "profile"

    user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.ForeignKey("user.id"),
    )
    user: sqlalchemy.orm.Mapped[User] = sqlalchemy.orm.relationship(
        "User",
    )
    first_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(100),
    )
    last_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(100),
    )
    avatar_url: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
