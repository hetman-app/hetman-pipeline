from enum import Enum
from typing import NamedTuple


class Flag(Enum):
    pass


class HandlerMode(Enum):
    ROOT = "ROOT"
    CONTEXT = "CONTEXT"
    ITEM = "ITEM"


class HandlerExpectedTypes(NamedTuple):
    value: tuple[type, ...]
    argument: tuple[type, ...]
