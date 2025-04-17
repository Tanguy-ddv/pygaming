"""The visual module contains the Visual class, an abstract for all object displayable on the screen."""
import pygame
from .child import Child
from .master import Master
from ..art import Art
from ...settings import Settings

class Graphical(Child):
    """The Graphicals are visual object having an art as main display."""

    def __init__(self, master: Master, art: Art, update_if_invisible: bool = False):
        super().__init__(master, update_if_invisible)
        self._art = art

    @property
    def width(self):
        return self._art.width

    @property
    def height(self):
        return self._art.height

    def start(self):
        """Call this method at the beginning of the phase."""
        self._art.start(**self.master.game.settings)
        self.notify_change()

    def end(self):
        """Call this method at the end of the phase."""
        self._art.end()

    def loop(self, dt: int):
        """Call this method at every loop iteration."""
        if self.is_visible() or self._update_if_invisible:
            has_changed = self._art.update(dt)
            if has_changed:
                self.notify_change()
            self.update(dt)

    def make_surface(self) -> pygame.Surface:
        """Create the image of the visual as a pygame surface."""
        return self
