import pygame
from .database import Texts, Speeches
from .database.database import SERVER, GAME
from .connexion import Client, EXIT
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

        self.soundbox = SoundBox()
        self.jukebox = Jukebox()
        
        self.inputs = Inputs()
        self.screen = Screen(*self.config.get("screen"))

        self.texts = Texts(self.database)
        self.speeches = Speeches(self.database)
        self.settings = Settings()

        self.settings.link_others(self.jukebox, self.soundbox, self.inputs.controls, self.texts, self.speeches, self.screen)

        if online:
            self.client = Client(self.config)
        else:
            self.client = None
        self.online = online

    def update(self) -> bool:
        """Update all the component of the game."""
        self.inputs.update()
        self.screen.display_phase(self.phases[self.current_phase])
        self.screen.update()
        self.jukebox.update()
        if self.online:
            self.client.update()
        is_game_over = self.update_phases()
        return self.inputs.quit or is_game_over or (self.online and self.client.is_server_killed())