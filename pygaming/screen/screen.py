"""The screen is the surface of the window."""

from ..settings import Settings
import pygame

class Screen:
    """The screen class is used to represent the screen of the game."""

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._fullscreen = False
        self.screen = pygame.display.set_mode((self._width, self._height))

    def update_settings(self, settings: Settings):
        """Update the screen with the settings."""
        self._fullscreen = settings.fullscreen
        if self._fullscreen:
            self.screen = pygame.display.set_mode((self._width, self._height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self._width, self._height))
        
    def display_phase(self, phase):
        """Blit the Frame on the screen."""
        self.screen.blit(phase.get_surface(self._width, self._height), (0,0))

    def update(self):
        """Update the screen"""
        pygame.display.flip()
