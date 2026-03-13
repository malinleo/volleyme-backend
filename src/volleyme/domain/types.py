import typing
import uuid

UserId = typing.NewType("UserId", uuid.UUID)
PlayerId = typing.NewType("PlayerId", uuid.UUID)
EventId = typing.NewType("EventId", uuid.UUID)
EventInvitationId = typing.NewType("EventInvitationId", uuid.UUID)
