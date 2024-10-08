"""The game module contains the game class which is used to represent every game."""
import pygame
from .database import Texts, Speeches
from .database.database import GAME
from .connexion import Client
from .inputs import Inputs, Mouse, Keyboard
from .settings import Settings
from .screen.screen import Screen
from .sound import SoundBox, Jukebox
from .base import BaseRunnable

class Game(BaseRunnable):
    """
    The game is the instance created and runned by the player.

    Params:
    ----
    first_phase: str, the name of the first frame.
    debug: bool
    """

    def __init__(self, first_phase: str, debug: bool = False) -> None:
        BaseRunnable.__init__(self, debug, GAME, first_phase)
        pygame.init()

        self.settings = Settings()
        self.soundbox = SoundBox(self.settings)
        self.jukebox = Jukebox(self.settings)

        self.mouse = Mouse(self.settings)
        self.keyboard = Keyboard()
        self._inputs = Inputs(self.mouse, self.keyboard)
        self._screen = Screen(self.config, self.settings)

        self.texts = Texts(self.database, self.settings, self.current_phase)
        self.speeches = Speeches(self.database, self.settings, self.current_phase)

        self.client = None
        self.online = False

    def update(self) -> bool:
        """Update all the component of the game."""
        loop_duration = self.clock.tick(self.config.get("max_frame_rate"))
        self.logger.update(loop_duration)
        self._inputs.update(loop_duration, self.current_phase)
        self._screen.display_phase(self.phases[self.current_phase])
        self._screen.update()
        self.jukebox.update()
        if self.online:
            self.client.update()
        is_game_over = self.update_phases(loop_duration)
        return self._inputs.quit or is_game_over or (self.online and self.client.is_server_killed())

    def connect(self) -> bool:
        """Connect the game to the server."""
        if not self.online:
            self.client = Client(self.config)
            self.online = True

    def disconnect(self) -> bool:
        """Disconnect the game from the server."""
        if self.online:
            self.client.close()
            self.client = None
            self.online = False
    
    def update_language(self, phase_name: str):
        self.texts = Texts(self.database, self.settings, phase_name)
        self.speeches = Speeches(self.database, self.settings, phase_name)
