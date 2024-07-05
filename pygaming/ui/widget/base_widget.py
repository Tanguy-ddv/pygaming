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
        frame.add_widget(self)
    
    def hide(self):
        """Hide the widget."""
        self.visible = False
    
    def show(self):
        """Show the widget."""
        self.visible = True
    
    def is_focused(self):
        """Overriden by the is_focus of the FocusSupport class if needed."""
        return False

    def focus(self):
        """Overriredn by the focus of the FocusSupport class if needed"""
        pass

    def unfocus(self):
        """Overriredn by the focus of the FocusSupport class if needed"""
        pass
    
    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be blitted."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, inputs: Inputs, loop_duration: int, x: int, y: int):
        """Update the widget with the inputs."""
        raise NotImplementedError()