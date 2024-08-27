"""The transition is used to go from one phase to another."""

from abc import ABC, abstractmethod
from typing import Any

class Transition(ABC):

    def __init__(self, game, previous_phase: str, next_phase: str) -> None:
        
        super().__init__()
        game.set_transition(previous_phase, next_phase, self)

    @abstractmethod
    def apply(self, phase) -> dict[str, Any]:
        """Get a dict with the value of the arguments passed to the start method of the next phase."""
        raise NotImplementedError()