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
        sqlalchemy.ForeignKey("user.id", name="fk_profile_user_id"),
    )
    user: sqlalchemy.orm.Mapped[User] = sqlalchemy.orm.relationship(
        "User",
        foreign_keys=[user_id],
        lazy="raise",
    )
    first_name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(100),
        nullable=True,
    )
    last_name: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(100),
        nullable=True,
    )
    avatar_url: sqlalchemy.orm.Mapped[str | None] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
        nullable=True,
    )

    @property
    def full_name(self) -> str | None:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None
