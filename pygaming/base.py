"""A BaseRunnable is an abstract object from which herit the game and the server."""
from abc import ABC, abstractmethod
from typing import Literal, Any
import pygame

from .logger import Logger
from .database import Database

from .config import Config
from .error import PygamingException
from .state import set_time_now, increment_counter

LEAVE = 'leave'
STAY = 'stay'


class BaseRunnable(ABC):
    """The BaseRunnable Class is an abstract class for both the Game and the Server."""

    def __init__(self, debug: bool, runnable_type: Literal['server', 'game'], first_phase: str) -> None:
        super().__init__()
        self.debug = debug
        self.config = Config()
        self.logger = Logger(self.config, debug)
        self.database = Database(self.config, runnable_type, debug)
        self.phases = {}
        self.transitions = {}
        self.current_phase = first_phase
        self.clock = pygame.time.Clock()
        increment_counter(f"launch_counter_{runnable_type}")
        set_time_now(f"last_launch_{runnable_type}")

    @abstractmethod
    def update(self):
        """Update the runnable, must be overriden."""
        raise NotImplementedError()

    def set_phase(self, name: str, phase):
        """Add a new phase to the game."""
        if not self.phases:
            self.current_phase = name
        if name in self.phases:
            raise PygamingException("This name is already assigned to another frame.")
        self.phases[name] = phase
        return self

    def update_phases(self, loop_duration: int):
        """Update the phases of the game."""
        # Update the current phase
        self.phases[self.current_phase].loop(loop_duration)
        # Ask what is next
        next_phase = self.phases[self.current_phase].next()
        # Verify if the phase is over
        if next_phase not in (LEAVE, STAY):
            # get the value for the arguments for the start of the next phase
            new_data = self.phases[self.current_phase].apply_transition(next_phase)
            # End the current phase
            self.phases[self.current_phase].finish()
            # change the phase
            self.current_phase = next_phase
            # start the new phase
            self.phases[self.current_phase].begin(**new_data)

        # if NO_NEXT was return, end the game.
        return next_phase == LEAVE

    def stop(self):
        """Stop the algorithm properly."""

    def run(self, **kwargs0: dict[str, Any]):
        """Run the game."""
        stop = False
        self.phases[self.current_phase].begin(**kwargs0)
        while not stop:
            stop = self.update()
        self.phases[self.current_phase].end()
        self.stop()
