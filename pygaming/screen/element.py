"""the element module contains the Element object, which is a base for every object displayed on the game window."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Union
import pygame
from ..phase import GamePhase
from .animated_surface import AnimatedSurface

# Anchors

TOP_RIGHT = 0, 1
TOP_LEFT = 0, 0
CENTER = 0.5, 0.5
BOTTOM_LEFT = 1, 0
BOTTOM_RIGHT = 1, 1

SurfaceLike = Union[AnimatedSurface, pygame.Surface]

class Element(ABC):
    """Element is the abstract class for everything object displayed on the game window: widgets, actors, decors, frames."""

    def __init__(
        self,
        master : Union[GamePhase | Element], # Frame or phase, no direct typing of frame to avoid circular import
        surface: SurfaceLike,
        x: int,
        y: int,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        layer: int = 0,
        hover_surface: Optional[pygame.Surface] = None,
        hover_cursor: Optional[pygame.Cursor] = None,
        can_be_disabled: bool = True,
        can_be_focused: bool = True
    ) -> None:
        """
        Create an Element.

        Params:
        ----
        master: Frame or Phase, the master of this object.
        surface: The surface.
        x, y: the coordinates in the master of the anchor point.
        anchor: the anchor point in % of the width and height. 
        width, height: the dimension of the object.
        layer: the layer of the object. The smaller the more on the background
        image_duration (ms): If a list is provided as background, the background of the frame is changed every image_duration.
        if image_duration is a list, it must have the same length as background.
        in this case, the i-th image of the background will be displayed image_duration[i] ms.
        image_introduction: int, if you provided a list for the surface, the background will not cycle back to 0
        but to this index. 
        hover_surface: Surface. If a surface is provided, it to be displayed at the mouse location when the
        frame is hovered by the mouse.
        hover_cursor: Cursor. If a cursor is provided, it is the cursor of the mouse when the mouse is over the frame.
        ca_be_disabled, can_be_focused: Some element could be disabled, like widgets. Some element could be focused.
        """

        self.layer = layer

        self.visible = True
        self.can_be_focused = can_be_focused
        self.focused = False
        self.can_be_disabled = can_be_disabled
        self.disabled = False

        if isinstance(surface, pygame.Surface):
            self.surface = AnimatedSurface([surface], 2, 0)
        else:
            self.surface = surface

        self.width, self.height = self.surface.width, self.surface.height
        self.x = x - anchor[0]*self.width
        self.y = y - anchor[1]*self.height
        ABC.__init__(self)
        self.master = master
        self.master.add_child(self)

        self.hover_cursor = hover_cursor
        self.hover_surface = hover_surface

    @property
    def absolute_x(self):
        """Return the absolute value of x in the game window."""
        return self.master.absolute_x + self.x

    @property
    def absolute_y(self):
        """Return the absolute value of y in the game window."""
        return self.master.absolute_y + self.y

    @property
    def game(self):
        """Return the game."""
        return self.master.game

    def update_hover(self, hover_x, hover_y): #pylint: disable=unused-argument
        """Update the hover cursor and surface. To be overriden by element needing it."""
        return False, None

    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be blitted."""
        raise NotImplementedError()

    def loop(self, loop_duration: int):
        """Update the element every loop iteration."""
        self.surface.update_animation(loop_duration)
        self.update(loop_duration)

    @abstractmethod
    def update(self, loop_duration: int):
        """Update the element logic every loop iteration."""
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
            self.switch_background()

    def disable(self):
        """disable the object if it can be disabled."""
        if self.can_be_disabled:
            self.disabled = True
            self.switch_background()

    def focus(self):
        """focus the object if it can be focused."""
        if self.can_be_focused:
            self.focused = False
            self.switch_background()

    def unfocus(self):
        """Unfocus the object if it can be focused."""
        if self.can_be_focused:
            self.focused = False
            self.switch_background()

    def switch_background(self):
        """
        Switch background when the widget is disabled, focused, enabled or unfocused.
        Don't do anything for basic elements, to be overriden by other elements.
        """


    @property
    def relative_coordinate(self):
        """Return the coordinate of the element in its frame."""
        return (self.x, self.y)

    @property
    def absolute_coordinate(self):
        """Return the coordinate of the element in the game window"""
        return (self.absolute_x, self.absolute_y)

    @property
    def relative_rect(self):
        """Return the rect of the element in its frame."""
        return pygame.rect.Rect(self.x, self.y, self.width, self.height)

    @property
    def absolute_rect(self):
        """Return the rect of the element in the game window."""
        return pygame.rect.Rect(self.absolute_x, self.absolute_y, self.width, self.height)

    @property
    def shape(self):
        """Return the shape of the element"""
        return (self.width, self.height)

    @property
    def relative_right(self):
        """Return the right coordinate of the element in the frame."""
        return self.x + self.width

    @property
    def absolute_right(self):
        """Return the right coordinate of the element in the game window"""
        return self.absolute_x + self.width

    @property
    def relative_bottom(self):
        """Return the bottom coordinate of the element in the frame."""
        return self.y + self.height

    @property
    def absolute_bottom(self):
        """Return the bottom coordinate of the element in the game window."""
        return self.absolute_y + self.height

    @property
    def relative_left(self):
        """Return the left coordinate of the element in the frame."""
        return self.x

    @property
    def absolute_left(self):
        """Return the left coordinate of the element in the game window."""
        return self.absolute_x

    @property
    def relative_top(self):
        """Return the top coordinate of the element in the frame."""
        return self.y

    @property
    def absolute_top(self):
        """Return the top coordinate of the element in the game window."""
        return self.absolute_y
