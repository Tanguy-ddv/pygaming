"""The abstract module contains abstract classes for object displayed on the screen."""
from typing import Callable
import pygame
from abc import ABC, abstractmethod
from .art import Art

class Visual(ABC):
    """The Visuals are object that can be seen on a screen."""

    def __init__(self, background: Art, update_if_invisible: bool = False):
        ABC.__init__(self)
        self.background = background
        self.width, self.height = background.size
        self._last_surface: pygame.Surface = None
        self._surface_changed: bool = True
        self.visible = True
        self._update_if_invisible = update_if_invisible
    
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be displayed."""
        if self._surface_changed:
            self._surface_changed = False
            self._last_surface = self.make_surface()
        return self._last_surface

    @abstractmethod
    def make_surface(self) -> pygame.Surface:
        """Create the image of the visual as a pygame surface."""

