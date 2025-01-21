"""The screen is the surface of the window."""

import pygame
from ..settings import Settings
from ..config import Config
from ..file import get_file

class Screen:
    """The screen class is used to represent the screen of the game."""

    def __init__(self, config: Config, settings: Settings) -> None:
        self._width, self._height = config.dimension
        self._fullscreen = settings.fullscreen
        self.screen = pygame.display.set_mode((self._width, self._height), pygame.FULLSCREEN if self._fullscreen else 0)

        pygame.display.set_caption(config.game_name)
        pygame.display.set_icon(pygame.image.load(get_file('', 'icon.ico')))

    def display_phase(self, phase):
        """Blit the Frame on the screen."""
        self.screen.blit(phase.get_surface(), (0,0))

    def update(self):
        """Update the screen."""
        pygame.display.flip()

    def update_settings(self, settings: Settings):
        """Update the screen based on the new settings."""
        if self._fullscreen != settings.fullscreen:
            self._fullscreen = settings.fullscreen
            self.screen = pygame.display.set_mode((self._width, self._height), pygame.FULLSCREEN if self._fullscreen else 0)
