"""The game module contains the game class which is used to represent every game."""
from threading import Thread
import pygame
from .database import TypeWriter, SoundBox, GAME
from .music import Jukebox
from .connexion import Client
from .inputs import Inputs, Mouse, Keyboard
from .settings import Settings
from .screen.screen import Screen
from ._base import BaseRunnable

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

        self.settings = Settings(self.config)

        self.soundbox = SoundBox(self.settings, first_phase, self.database)
        self.jukebox = Jukebox(self.settings)

        self.typewriter = TypeWriter(self.database, self.settings, first_phase)

        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self._inputs = Inputs(self.mouse, self.keyboard)

        self._screen = Screen(self.config, self.settings)

        self.client = None
        self.online = False

        self.screen_clock = pygame.time.Clock()
        self._display_screen = True
        self._pause_display = False
        self._display_screen_thread = Thread(target=self.display_image)

    def start(self):
        """Call this method at the beginning of the run."""
        self._display_screen_thread.start()

    def transition(self, next_phase):
        # Pause the displaying thread
        self._pause_display = True
        # get the value for the arguments for the start of the next phase
        new_data = self.phases[self.current_phase].apply_transition(next_phase)

        # End the current phase
        self.phases[self.current_phase].finish()
        # change the phase
        self.current_phase = next_phase
        # start the new phase
        self.phases[self.current_phase].begin(**new_data)
        # Resume the displaying thread
        self._pause_display = False

    def display_image(self) -> bool:
        """Display the image."""
        while self._display_screen:
            loop_duration = self.screen_clock.tick(self.config.get("max_frame_rate"))
            if not self._pause_display:
                self._screen.display_phase(self.phases[self.current_phase])
                self._screen.update()
                self.phases[self.current_phase].update_hover(loop_duration)

    def update(self) -> bool:
        """Update all the component of the game."""
        loop_duration = self.clock.tick(self.config.get("game_frequency"))
        self.logger.update(loop_duration)
        self._inputs.update(loop_duration)
        self.jukebox.update()
        if self.online:
            self.client.update()
        is_game_over = self.update_phases(loop_duration)
        return self._inputs.quit or is_game_over or (
            self.online and self.client.is_server_killed() and self.config.get("stop_game_on_server_killed", False)
        )

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
        self.keyboard.update_settings(self.settings)
        self.jukebox.update_settings(self.settings)

    def stop(self):
        """Stop the algorithm properly"""
        self.database.close()
        self.disconnect()
        self._display_screen = False # Stop the thread displaying the screen.
        self._display_screen_thread.join() # And wait for it to complete.
        pygame.quit()
