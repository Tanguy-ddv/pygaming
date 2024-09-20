"""A BaseRunnable is an abstract object from which herit the game and the server."""
from abc import ABC, abstractmethod
from typing import Literal, Any
import pygame

from .logger import Logger
from .database import Database

from .config import Config
from .error import PygamingException

NO_NEXT = 'no_next'
STAY = 'stay'


class BaseRunnable(ABC):
    """The BaseRunnable Class is an abstract class for both the Game and the Server."""

    def __init__(self, debug: bool, runnable_type: Literal['server', 'game']) -> None:
        super().__init__()
        pygame.init()
        self.debug = debug
        self.config = Config()
        self.logger = Logger(self.config, debug)
        self.database = Database(self.config, runnable_type, debug)
        self.phases = {}
        self.transitions = {}
        self.current_phase = ""
        self.clock = pygame.time.Clock()

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

    def set_transition(self, phase1: str, phase2: str, transition):
        """
        Set a transition between two phases.

        Params:
        ----
        phase1: the name of the phase that is ending.
        phase2: the name of the phase that is starting.
        transition: the Transition object between the two phases.
        Returns:
        ----
        The game itself for method chaining
        """
        self.transitions[(phase1, phase2)] = transition
        return self

    def update_phases(self, loop_duration: int):
        """Update the phases of the game."""
        self.phases[self.current_phase].loop(loop_duration)
        next_phase = self.phases[self.current_phase].next()
        # Verify if the phase is over
        if next_phase not in [NO_NEXT, STAY]:
            # if it is, end the current phase
            self.phases[self.current_phase].end()
            # get the value for the arguments for the start of the next phase
            new_data = self.transitions[(self.current_phase, next_phase)].apply(
                self.phases[self.current_phase]
            )
            # change the phase
            self.current_phase = next_phase
            # start the new phase
            self.phases[self.current_phase].start(**new_data)

        # if NO_NEXT was return, end the game.
        return next_phase == NO_NEXT

    def stop(self):
        """Stop the algorithm properly."""

    def run(self, **kwargs0: dict[str, Any]):
        """Run the game."""
        stop = False
        self.phases[self.current_phase].start(**kwargs0)
        while not stop:
            stop = self.update()
        self.phases[self.current_phase].end()
        self.stop()
        pygame.quit()
