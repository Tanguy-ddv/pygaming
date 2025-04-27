"""
The states module contains the State enum, base class for all states,
and the WidgetStates enum
"""
from enum import Enum, auto

class States(Enum):
    pass

class WidgetStates(States):

    NORMAL = auto()
    FOCUSED = auto()
    DISABLED = auto()
    HOVERED = auto()
    ACTIVE = auto() # for button currently active
    EMPTY = auto() # for entries current empty
