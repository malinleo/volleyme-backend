import enum


class GameType(enum.IntEnum):
    VOLLEYBALL = 0


class EventFormatType(enum.IntEnum):
    DEFAULT = 0
    RATING = 1
    TRAINING = 2


class EventParticipantRole(enum.IntEnum):
    HOST = 0
    PARTICIPANT = 1
    NOBODY = 2
