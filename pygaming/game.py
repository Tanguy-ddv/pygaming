"""The game module contains the game class which is used to represent every game."""
import pygame
from .database import TypeWriter, SoundBox, GAME
from .music import Jukebox
from .connexion import Client
from .inputs import Inputs, Mouse, Keyboard
from .settings import Settings
from .screen.screen import Screen
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

        self.soundbox = SoundBox(self.settings, first_phase, self.database)
        self.jukebox = Jukebox(self.settings)

        self.typewriter = TypeWriter(self.database, self.settings, first_phase)

        self.mouse = Mouse(self.settings)
        self.keyboard = Keyboard()
        self._inputs = Inputs(self.mouse, self.keyboard)

        self._screen = Screen(self.config, self.settings)

        self.client = None
        self.online = False

    def update(self) -> bool:
        """Update all the component of the game."""
        loop_duration = self.clock.tick(self.config.get("max_frame_rate"))
        self.logger.update(loop_duration)
        self._inputs.update(loop_duration)
        self._screen.display_phase(self.phases[self.current_phase])
        self._screen.update()
        self.jukebox.update()
        if self.online:
            self.client.update()
        is_game_over = self.update_phases(loop_duration)
        return self._inputs.quit or is_game_over or (self.online and self.client.is_server_killed() and self.config.get("stop_game_on_server_killed", False))

    def connect(self, initial_message_header = None, initial_message_payload = None) -> bool:
        """Connect the game to the server."""
        if not self.online:
            self.client = Client(self.config, self.logger, initial_message_header, initial_message_payload) 
            if not self.client.is_connected:
                self.disconnect()
            else:
                self.online = True
        return self.online

    def disconnect(self):
        """Disconnect the game from the server."""
        if self.online:
            self.client.close()
            self.client = None
            self.online = False

    def update_settings(self):
        """Update the language."""
        self.typewriter.update_settings(self.settings, self.current_phase)
        self.soundbox.update_settings(self.settings, self.current_phase)
        self.keyboard.update_settings()

    def stop(self):
        """Stop the algorithm properly"""
        self.database.close()
        self.disconnect()
        pygame.quit()
