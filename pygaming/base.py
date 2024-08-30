"""A base is an abstract object from which herit the game and the server."""

NO_NEXT = 'no_next'
from typing import Literal
import sys

from .logger import Logger
from .database import Database
from .settings import Settings

from .config import Config
from .error import PygamingException

import pygame
from abc import ABC, abstractmethod

class BaseRunnable(ABC):

    def __init__(self, debug: bool, type: Literal['server', 'game']) -> None:
        super().__init__()
        pygame.init()
        self.debug = debug
        self.logger = Logger(debug)
        self.config = Config()
        self.max_fps = self.config.get("max_frame_rate")
        self.database = Database(self.config, type, debug)
        self.phases = {}
        self.transitions = {}
        self.current_phase = ""
        self.clock = pygame.time.Clock()

    @abstractmethod
    def update(self):
        raise NotImplementedError()

    def set_phase(self, name: str, phase):
        """Add a new phase to the game."""
        if not len(self.phases.keys()):
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
    
    def update_phases(self):
        loop_time = self.clock.tick(self.max_fps)
        self.phases[self.current_phase].update(loop_time)
        next_phase = self.phases[self.current_phase].next()
        if next_phase and next_phase != NO_NEXT:
            self.phases[self.current_phase].end()
            new_data = self.transitions[(self.current_phase, next_phase)].apply(
                self.phases[self.current_phase]
            )
            self.current_phase = next_phase
            self.phases[self.current_phase].start(**new_data)

        return next_phase == NO_NEXT

    def stop(self):
        """Stop the algorithm properly."""

    def run(self):
        """Run the game."""
        stop = False
        while not stop:
            stop = self.update()
        self.phases[self.current_phase].end()
        self.stop()
        pygame.quit()
        sys.exit()