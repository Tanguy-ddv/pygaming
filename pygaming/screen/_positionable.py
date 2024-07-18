from abc import ABC, abstractmethod
import pygame
from ..inputs import Inputs
from ._backgrounds import BackgroundsLike, Backgrounds

class Positionable(ABC):
    """Positionable is the abstract class for everything having a position: widgets, actors, decors, frames."""

    def __init__(self, master, backgrounds: BackgroundsLike, x: int, y: int, width: int, height: int, layer: int = 0) -> None:
        """
        Create an object.

        Params:
        ----
        master: Frame or Phase, the master of this object.
        backgrounds: The backgrounds.
        x, y: the coordinates in the master.
        width, height: the dimension of the object.
        layer: the layer of the object. The smaller the more on the background
        """
        self.x = x
        self.y = y
        self.layer = layer
        self.visible = True
        self.can_be_focused = False
        self.can_be_disabled = False
        self.width = width
        self.height = height
        self.backgrounds = Backgrounds(width, height, backgrounds, can_be_focused=self.can_be_focused, can_be_disabled=self.can_be_disabled)
        ABC.__init__(self)
        self.frame = master
        master.add_positionable(self)
    
    @property
    def absolute_x(self):
        return self.master.absolute_x + self.x
    
    @property
    def absolute_y(self):
        return self.master.absolute_y + self.y

    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be blitted."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, inputs: Inputs, loop_duration: int, x: int, y: int):
        """Update the widget with the inputs."""
        raise NotImplementedError()
    
    def move(self, new_x: int, new_y: int):
        """Move the object."""
        self.x = new_x
        self.y = new_y
    
    def set_layer(self, new_layer: int):
        """Set a new value for the layer"""
        self.layer = new_layer
    
    def send_to_the_back(self):
        """Send the object one step to the back."""
        self.layer -= 1
    
    def send_to_the_front(self):
        """Send the object one step to the front."""
        self.layer += 1
    
    def hide(self):
        """Hide the object."""
        self.visible = False
    
    def show(self):
        """Show the object."""
        self.visible = True
    
    def enable(self):
        """Enable the object if it can be disabled."""
        if self.can_be_disabled:
            self.disabled = False

    def disable(self):
        """disable the object if it can be disabled."""
        if self.can_be_disabled:
            self.disabled = True
    
    def focus(self):
        """focus the object if it can be focused."""
        if self.can_be_focused:
            self.focused = False
        
    def unfocus(self):
        """Unfocus the object if it can be focused."""
        if self.can_be_focused:
            self.focused = False
    
    @property
    def coordinate(self):
        return (self.x, self.y)

    @property
    def absolute_coordinate(self):
        return (self.absolute_x, self.absolute_y)