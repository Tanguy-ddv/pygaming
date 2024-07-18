"""The screen is the surface of the window."""

from .._settings import Settings
from ..phase import Phase
import pygame

class Screen:
    """The screen class is used to store the screen of the game."""

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
        
    def blit_phase(self, phase: Phase):
        """Blit the Frame on the screen."""
        for frame in sorted(phase.frames, key= lambda f: f.layer):
            self.screen.blit(frame.get_surface(), frame.top_left)

    def update(self):
        """Update the screen"""
        pygame.display.flip()
