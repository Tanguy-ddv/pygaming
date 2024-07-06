from abc import ABC, abstractmethod
import pygame
from ..inputs import Inputs
from ..positionable import Positionable

class BaseWidget(ABC, Positionable):

    def __init__(self, frame, x: int, y: int, layer: int = 0) -> None:
        ABC.__init__(self)
        Positionable.__init__(self, x, y, layer)
        self.frame = frame
        self.visible = True
        self.can_be_focused = False
        self.can_be_disabled = False
        frame.add_widget(self)
    
    def hide(self):
        """Hide the widget."""
        self.visible = False
    
    def show(self):
        """Show the widget."""
        self.visible = True

    def _get_background(self) -> pygame.Surface:
        """Return the background."""
        if self.can_be_disabled and self.is_disabled():
            return self._disable_background.copy()
        elif self.can_be_focused and self.is_focused():
            return self._focus_background.copy()
        return self._background.copy()

    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be blitted."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, inputs: Inputs, loop_duration: int, x: int, y: int):
        """Update the widget with the inputs."""
        raise NotImplementedError()