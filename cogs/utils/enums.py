from enum import Enum

__all__ = ['Action']


class Action(Enum):
    KICK = 1
    BAN = 2
    MISC = 3
    UNBAN = 4
