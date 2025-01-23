"""The visual module contains the Visual class, an abstract for all object displayable on the screen."""
import pygame
from abc import ABC, abstractmethod
from .art import Art
from ..settings import Settings

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

    def begin(self, settings: Settings):
        """Call self method at the beginning of the phase."""
        self.background.start(settings)
    
    def finish(self):
        """Call self method at the end of the phase."""
        self.background.unload()

    @abstractmethod
    def make_surface(self) -> pygame.Surface:
        """Create the image of the visual as a pygame surface."""

