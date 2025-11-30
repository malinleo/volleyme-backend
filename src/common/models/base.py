import datetime
import uuid
import sqlalchemy.orm


class Base(sqlalchemy.orm.DeclarativeBase):
    """Base class to inherit models from."""


class BaseModel(Base):
    """Base model."""

    __abstract__ = True


class TimeStampedModel(BaseModel):
    """Model with create and update timestamps."""

    __abstract__ = True

    created_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.text("now()"),
    )
    updated_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.mapped_column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.text("now()"),
        server_onupdate=sqlalchemy.text("now()"),
    )


class IDModel(BaseModel):
    """Model with id."""

    __abstract__ = True

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        sqlalchemy.UUID,
        default=uuid.uuid4,
        primary_key=True,
    )
