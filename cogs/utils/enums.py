from enum import Enum

__all__ = ['Change', 'Action']


class Change(Enum):
    CLOVER = 1
    MEMBER = 2
    PROMOTION = 3


class Action(Enum):
    MUTE = 1
    KICK = 2
    SOFTBAN = 3
    BAN = 4
    UNBAN = 5
