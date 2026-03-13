import datetime
import uuid

from src.common import dto


class InvitationDetailDto(dto.BaseDto):
    id: uuid.UUID
    event_id: uuid.UUID
    user_id: uuid.UUID | None = None
    token: str
    expires_at: datetime.datetime | None = None
    used_at: datetime.datetime | None = None
