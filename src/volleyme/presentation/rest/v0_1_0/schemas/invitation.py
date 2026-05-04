import datetime
import uuid

from src.common import schemas


class InvitationCreateSchema(schemas.BaseSchema):
    event_id: uuid.UUID


class InvitationDetailSchema(schemas.BaseSchema):
    id: uuid.UUID
    event_id: uuid.UUID
    user_id: uuid.UUID | None = None
    token: str
    expires_at: datetime.datetime | None = None
    used_at: datetime.datetime | None = None
