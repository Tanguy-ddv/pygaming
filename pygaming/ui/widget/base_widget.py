from abc import ABC, abstractmethod
import pygame
from ..inputs import Inputs

class BaseWidget(ABC):

    def __init__(self, frame, x: int, y: int, width: int, height: int, background: pygame.Surface, initial_focus: bool = False) -> None:
        super().__init__()
        self._focus = initial_focus
        self.frame = frame
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background = background.subsurface((0,0, width, height))
        self.visible = True
    
    def focus(self):
        self._focus = True
    
    def unfocus(self):
        self._focus = False
    
    def hide(self):
        self.visible = False
    
    def show(self):
        self.visible = True
    
    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be blitted."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, inputs: Inputs, loop_duration: int, **kwargs):
        """Update the widget with the inputs."""
        raise NotImplementedError()

    def move(self, new_x, new_y):
        """Move the widget on the frame."""
        self.x = new_x
        self.y = new_y