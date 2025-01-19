"""the element module contains the Element object, which is a base for every object displayed on the game window."""
from abc import ABC, abstractmethod
from typing import Optional, Union
import pygame
from ..phase import GamePhase
from .art.art import Art
from ..error import PygamingException
from .mask import Mask
from .anchors import TOP_LEFT
from ..inputs import Click
from ..cursor import Cursor

class Element(ABC):
    """Element is the abstract class for everything object displayed on the game window: widgets, actors, decors, frames."""

    def __init__(
        self,
        master: Union[GamePhase, 'Element'], # Frame or phase, no direct typing of frame to avoid circular import
        surface: Art,
        x: int,
        y: int,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        layer: int = 0,
        hover_surface: Optional[Art] = None,
        hover_cursor: Optional[Cursor] = None,
        can_be_disabled: bool = True,
        can_be_focused: bool = True,
        active_area: Optional[Mask | pygame.Mask] = None
    ) -> None:
        """
        Create an Element.

        Params:
        ----
        - master: Frame or Phase, the master of this object.
        - surface: The surface. It is an Art
        - x, int, the coordinates in the master of the anchor point.
        - y: int, the coordinates in the master of the anchor point.
        - anchor: the anchor point in % of the width and height. 
        - hover_surface: Surface. If a surface is provided, it to be displayed at the mouse location when the
        frame is hovered by the mouse.
        - hover_cursor: Cursor. If a cursor is provided, it is the cursor of the mouse when the mouse is over the element.
        - can_be_disabled: some element can be disabled.
        - can_be_focused: Some element can be focused.
        """

        self.layer = layer
        self.visible = True
        self.can_be_focused = can_be_focused
        self.focused = False
        self.can_be_disabled = can_be_disabled
        self.disabled = False

        self.surface = surface
        if not active_area is None and active_area.get_size() != self.surface.size:
            raise PygamingException("The active area must have the same size than the art.")
        self._active_area = active_area

        self.width, self.height = self.surface.width, self.surface.height
        self._x = x
        self._y = y
        self.anchor = anchor
        ABC.__init__(self)
        self.master = master
        self.master.add_child(self)

        self.hover_cursor = hover_cursor
        self.hover_surface = hover_surface

        self._last_surface: pygame.Surface = None
        self._surface_changed: bool = True
    
    def move(self, new_x: int = None, new_y: int = None, new_anchor: tuple[float, float] = None):
        """
        Move the element in the master frame.
        
        Params:
        ---
        - new_x: int = None. If specified, change the current x of the element. Otherwise do not change it.
        - new_y: int = None. If specified, change the current y of the element. Otherwise do not change it.
        - new_anchore: tuple[float, float] = None. If specified, change the current anchor of the element. Otherwise do not change it.
        """
        if not new_anchor is None:
            self.anchor = new_anchor
        if not new_y is None:
            self._y = new_y
        if not new_x is None:
            self._x = new_x
        
        self.notify_change()

    def is_contact(self, mouse_pos: Optional[tuple[int, int] | Click]):
        """Return True if the mouse is hovering the element."""
        if mouse_pos is None:
            return False
        elif isinstance(mouse_pos, Click):
            x, y = mouse_pos.x, mouse_pos.y
        else:
            x, y = mouse_pos
        x -= self.absolute_left
        y -= self.absolute_top
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return bool(self._active_area.get_at((x,y)))

    @property
    def game(self):
        """Return the game."""
        return self.master.game

    def update_hover(self):
        """Update the hover cursor and surface."""
        return self.hover_surface.get() if self.hover_surface else None, self.hover_cursor.get(self.game.settings) if self.hover_cursor else None

    def get_surface(self) -> pygame.Surface:
        """Return the surface to his parent."""
        if self._surface_changed:
            self._last_surface = self.make_surface()
            self._surface_changed = False
        return self._last_surface

    @abstractmethod
    def make_surface(self) -> pygame.Surface:
        """Make the new surface to be returned to his parent."""
        raise NotImplementedError()

    def notify_change(self):
        """Notify the need to remake the last surface."""
        self._surface_changed = True
        self.master.notify_change()

    def loop(self, loop_duration: int):
        """Update the element every loop iteration."""
        if self.hover_surface:
            self.hover_surface.update(loop_duration)
        if self.hover_cursor:
            self.hover_cursor.update(loop_duration)
        has_changed = self.surface.update(loop_duration)
        if has_changed:
            self.notify_change()
        self.update(loop_duration)

    def begin(self):
        """Execute this method at the beginning of the phase to load the active area and the surface before running class-specific start method."""
        if isinstance(self._active_area, Mask):
            self._active_area.load(self.game.settings)
        elif self._active_area is None:
            self.surface.set_load_on_start()
            self.surface.start(self.game.settings)
            self._active_area = pygame.mask.from_surface(self.surface.surfaces[0], 127)
        self.notify_change()
        self.start()

    @abstractmethod
    def start(self):
        """Execute this method at the beginning of the phase."""
        raise NotImplementedError()

    def finish(self):
        """Execute this method at the end of the phase, unload the main art and the active area. Call the class-specific end method."""
        self.surface.unload()
        if isinstance(self._active_area, Mask):
            self._active_area.unload()
        self.end()

    @abstractmethod
    def end(self):
        """Execute this method at the end of the phase."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, loop_duration: int):
        """Update the element logic every loop iteration."""
        raise NotImplementedError()

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
        self.master.notify_change()

    def show(self):
        """Show the object."""
        self.visible = True
        self.master.notify_change()
    
    def is_visible(self):
        """Return wether the widget is visible or not."""
        return self.visible and self.master.is_visible()

    def enable(self):
        """Enable the object if it can be disabled."""
        if self.can_be_disabled and self.disabled:
            self.disabled = False
            self.switch_background()

    def disable(self):
        """disable the object if it can be disabled."""
        if self.can_be_disabled and not self.disabled:
            self.disabled = True
            self.switch_background()

    def focus(self):
        """focus the object if it can be focused."""
        if self.can_be_focused and not self.focused:
            self.focused = True
            self.switch_background()

    def unfocus(self):
        """Unfocus the object if it can be focused."""
        if self.can_be_focused and self.focused:
            self.focused = False
            self.switch_background()

    def switch_background(self):
        """
        Switch background when the widget is disabled, focused, enabled or unfocused.
        Don't do anything for basic elements, to be overriden by other elements.
        """
        self.notify_change()

    @property
    def relative_coordinate(self):
        """Reutnr the relative coordinate of the element in its frame."""
        return (self.relative_left, self.relative_top)

    @property
    def absolute_coordinate(self):
        """Return the coordinate of the element in the game window."""
        return (self.absolute_left, self.absolute_top)

    @property
    def relative_rect(self):
        """Return the rect of the element in its frame."""
        return pygame.rect.Rect(self.relative_left, self.relative_top, self.width, self.height)

    @property
    def absolute_rect(self):
        """Return the rect of the element in the game window."""
        return pygame.rect.Rect(self.absolute_left, self.absolute_top, self.width, self.height)

    @property
    def shape(self):
        """Return the shape of the element"""
        return (self.width, self.height)

    @property
    def relative_right(self):
        """Return the right coordinate of the element in the frame."""
        return self.relative_left + self.width

    @property
    def absolute_right(self):
        """Return the right coordinate of the element in the game window"""
        return self.absolute_left + self.width

    @property
    def relative_bottom(self):
        """Return the bottom coordinate of the element in the frame."""
        return self.relative_top + self.height

    @property
    def absolute_bottom(self):
        """Return the bottom coordinate of the element in the game window."""
        return self.absolute_top + self.height

    @property
    def relative_left(self):
        """Return the left coordinate of the element in the frame."""
        return self._x - self.anchor[0]*self.width

    @property
    def absolute_left(self):
        """Return the left coordinate of the element in the game window."""
        return self.master.absolute_left + self.relative_left

    @property
    def relative_top(self):
        """Return the top coordinate of the element in the frame."""
        return self._y - self.anchor[1]*self.height

    @property
    def absolute_top(self):
        """Return the top coordinate of the element in the game window."""
        return self.master.absolute_top + self.relative_top
