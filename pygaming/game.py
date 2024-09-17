"""The game module contains the game class which is used to represent every game."""
import pygame
from .database import Texts, Speeches
from .database.database import GAME
from .connexion import Client
from .inputs import Inputs
from .settings import Settings
from .screen.screen import Screen
from .sound import SoundBox, Jukebox
from .base import BaseRunnable

class Game(BaseRunnable):
    """
    The game is the instance created and runned by the player.
    It can be online (with a server) or offline.
    """

    def __init__(self, online: bool = True, debug: bool = False) -> None:
        BaseRunnable.__init__(self, debug, GAME)
        pygame.init()

        self.settings = Settings()
        self.soundbox = SoundBox(self.settings)
        self.jukebox = Jukebox(self.settings)

        self.inputs = Inputs(self.settings)
        self._screen = Screen(self.config, self.settings)

        self.texts = Texts(self.database, self.settings)
        self.speeches = Speeches(self.database, self.settings)

        if online:
            self.client = Client(self.config)
        else:
            self.client = None
        self.online = online

    def update(self) -> bool:
        """Update all the component of the game."""
        loop_duration = self.clock.tick(self.config.get("max_frame_rate"))
        self.logger.update(loop_duration)
        self.inputs.update()
        self._screen.display_phase(self.phases[self.current_phase])
        self._screen.update()
        self.jukebox.update()
        if self.online:
            self.client.update()
        is_game_over = self.update_phases(loop_duration)
        return self.inputs.quit or is_game_over or (self.online and self.client.is_server_killed())
