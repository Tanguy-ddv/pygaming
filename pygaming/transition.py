from abc import ABC, abstractmethod
from .game import Game
from .server import Server
from .phase import GamePhase, ServerPhase
from typing import Any

class GameTransition(ABC):

    def __init__(self, game: Game, previous_phase: str, next_phase: str) -> None:
        ABC.__init__(self)
        game.set_transition(previous_phase, next_phase, self)
    
    @abstractmethod
    def apply(self, phase: GamePhase) -> dict[str, Any]:
        """
        Apply the transition between the two phases by extracting a dict from the ending phase.
        The keys of the dict are the argument name of the .start(...) method of the starting phase.
        The values are the values of the argument passed to the .start(...) method

        Example:
        >>> class Phase0(GamePhase):
        >>>     a: int
        >>>     b: float

        >>> class Phase1(GamePhase):            
        >>>     def start(self, a: int, b: float):
        >>>         ....

        >>> class Transition01(GameTransition):
        >>>    def apply(self, phase0: Phase0):
        >>>         retun {'a' : phase0.a, 'b': phase0.a + phase0.b**2}
        """
        raise NotImplementedError()

class ServerTransition(ABC):

    def __init__(self, server: Server, previous_phase: str, next_phase: str) -> None:
        ABC.__init__(self)
        server.set_transition(previous_phase, next_phase, self)
    
    @abstractmethod
    def apply(self, phase: ServerPhase) -> dict[str, Any]:
        """
        Apply the transition between the two phases by extracting a dict from the ending phase.
        The keys of the dict are the argument name of the .start(...) method of the starting phase.
        The values are the values of the argument passed to the .start(...) method

        Example:
        >>> class Phase0(ServerPhase):
        >>>     a: int
        >>>     b: float

        >>> class Phase1(ServerPhase):            
        >>>     def start(self, a: int, b: float):
        >>>         ....

        >>> class Transition01(ServerTransition):
        >>>    def apply(self, phase0: Phase0):
        >>>         retun {'a' : phase0.a, 'b': phase0.a + phase0.b**2}
        """
        raise NotImplementedError()