from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm
from src.common.models import base as base_models
import typing

if typing.TYPE_CHECKING:
    from .profile import Profile


class User(
    base_models.IDModel,
    base_models.TimeStampedModel,
):
    __tablename__ = "user"

    email: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.String(254),
        unique=True,
    )
    password: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text,
    )
    profile: sqlalchemy.orm.Mapped[Profile] = sqlalchemy.orm.relationship(
        "Profile",
        back_populates="user",
    )
