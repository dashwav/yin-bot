from enum import Enum

__all__ = ['Change', 'Action']


class Change(Enum):
    CLOVER = 1
    MEMBER = 2
    PROMOTION = 3


class Action(Enum):
    KICK = 1
    BAN = 2
