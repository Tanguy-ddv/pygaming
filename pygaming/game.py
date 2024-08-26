import pygame
NO_NEXT = 'no_next'
from .error import PygamingException
from typing import Callable, Any
from .database import Database, Texts, Speeches
from .connexion import Client
from .logger import Logger
from .inputs import Inputs
from .config import Config
from .settings import Settings
from .screen.screen import Screen
from .sound import SoundBox, Jukebox

class Game:
    """
    The game is the instance created and runned by the player.
    It can be online (with a server) or offline.
    """

    def __init__(self, width: int, height: int, online: bool = True, debug: bool = False) -> None:
        pygame.init()
        self.config = Config()

        self.soundbox = SoundBox()
        self.jukebox = Jukebox()
        
        self.inputs = Inputs()
        self.screen = Screen(width, height)

        self.database = Database(self.config, debug)
        self.texts = Texts(self.database)
        self.speeches = Speeches(self.database)

        self.settings = Settings(self.jukebox, self.soundbox, self.inputs.controls, self.texts, self.speeches, self.screen)

        self.logger = Logger()
        self.clock = pygame.time.Clock()

        if online:
            self.client = Client()
        
        self.phases: dict[str] = {}
        self.transitions: dict[tuple[str, str], Callable[[Any], dict[str, Any]]] = {}
        self.current_phase = ""

    def set_phase(self, name: str, phase):
        """Add a new phase to the game."""
        if not len(self.phases.keys()):
            self.current_phase = name
        if name in self.phases:
            raise PygamingException("This name is already assigned to another frame.")
        self.phases[name] = phase
        return self
    
    def set_transition(self, phase1: str, phase2: str, transition_function: Callable[[Any], dict[str, Any]]):
        """
        Set a transition between two phases.

        Params:
        ----
        phase1: the name of the phase that is ending.
        phase2: the name of the phase that is starting
        transition_function: a function that calculate the data that will be passed as the argument of the start method of the new phase.
            - The unique argument of this function is the phase, the attributes of the game might be accessed direclty through the phase.
            - The ouput of this function must be a dict. The keys are the name of the argument of the start method of the new phase,
            the values are the values for these arguments.
        Returns:
        ----
        The game itself for method chaining
        """
        self.transitions[(phase1, phase2)] = transition_function
        return self

    def update(self) -> bool:
        """Update all the component of the game."""
        self.inputs.update()
        self.screen.update()
        self.jukebox.update()
        loop_time = self.clock.tick()
        self.phases[self.current_phase].update(loop_time)
        next_phase = self.phases[self.current_phase].next()
        if next_phase and next_phase != NO_NEXT:
            self.phases[self.current_phase].end()
            new_data = self.transitions[(self.current_phase, next_phase)](
                self.phases[self.current_phase],
                self,
            )
            self.current_phase = next_phase
            self.phases[self.current_phase].start(self, **new_data)

        return self.inputs.quit or next_phase == NO_NEXT

    def end(self):
        """Call this function at the end of the game."""

    def run(self):
        """Run the game."""
        stop = False
        while not stop:
            stop = self.update()
        pygame.quit()