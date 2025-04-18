"""the element module contains the Element object, which is a base for every object displayed on the game window."""
from abc import abstractmethod
from typing import Optional
import pygame
from ._abstract import Master, Graphical, Placable
from .tooltip import Tooltip
from .art import Art
from ..inputs import Click
from .cursor import Cursor
from .hitbox import Hitbox

class Element(Graphical, Placable):
    """Element is the abstract class for everything object displayed on the game window: widgets, actors, frames."""

    def __init__(
        self,
        master: Master,
        art: Art,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        can_be_disabled: bool = True,
        can_be_focused: bool = True,
        active_area: Optional[Hitbox] = None,
        update_if_invisible: bool = False
    ) -> None:
        """
        Create an Element.

        Params:
        ----
        - master: Master, the master of this object.
        - background: The background. It is an Art
        - tooltip: Tooltip. If a surface is provided, it to be displayed at the mouse location when the
        frame is hovered by the mouse.
        - cursor: Cursor. If a cursor is provided, it is the cursor of the mouse when the mouse is over the element.
        - can_be_disabled: some element can be disabled.
        - can_be_focused: Some element can be focused.
        - active_area
        - update_if_invisible
        """

        super().__init__(master, art, update_if_invisible)
        self.visible = True
        self.can_be_focused = can_be_focused
        self.focused = False
        self.can_be_disabled = can_be_disabled
        self.disabled = False

        if active_area is None:
            active_area = Hitbox(0, 0, *self._art.size)
        self._active_area = active_area

        self._cursor = cursor
        self._tooltip = tooltip

    @property
    def background(self):
        return self._art

    def is_contact(self, pos: Optional[Click | tuple[int, int]]):
        """Return whether the position, relative to the top left of the master of this element, is in contact with the element."""
        if pos is None or not self.on_master:
            return False
        if isinstance(pos, tuple):
            pos = Click(*pos)
        ck = pos.make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio)
        self._active_area.load(self.game.settings)
        return self._active_area.is_contact((ck.x, ck.y))

    @property
    def game(self):
        """Return the game."""
        return self.master.game

    def get_hover(self):
        """Update the hover cursor and tooltip."""
        return self._tooltip, self._cursor

    def notify_change(self):
        """Notify the need to remake the last surface."""
        self._surface_changed = True
        if self.on_master:
            self.master.notify_change()

    def loop(self, loop_duration: int):
        """Update the element every loop iteration."""
        if (self.on_master and self.is_visible()) or self._update_if_invisible:
            Graphical.loop(self, loop_duration)
            self.update(loop_duration)

    def begin(self):
        """
        Execute this method at the beginning of the phase
        to load the active area and the background before running class-specific start method.
        """
        self._active_area.load(self.game.settings)
        Graphical.begin(self)
        self.start()

    def unset_hover(self):
        pass

    @abstractmethod
    def start(self):
        """Execute this method at the beginning of the phase."""
        raise NotImplementedError()

    def finish(self):
        """Execute this method at the end of the phase, unload the main art and the active area. Call the class-specific end method."""
        self.end()
        Graphical.finish(self)
        self._active_area.unload()

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
        self.master.notify_change()

    def send_to_the_back(self):
        """Send the object one step to the back."""
        self.layer -= 1
        self.master.notify_change()

    def send_to_the_front(self):
        """Send the object one step to the front."""
        self.layer += 1
        self.master.notify_change()

    def hide(self):
        """Hide the object."""
        self.visible = False
        self.master.notify_change()
        return self

    def show(self):
        """Show the object."""
        self.visible = True
        self.master.notify_change()

    def is_visible(self):
        """Return wether the widget is visible or not."""
        return self.visible and self._x is not None and self.master.is_visible()

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
        return pygame.rect.Rect(self.absolute_left, self.absolute_top, self.width*self.master.wc_ratio[0], self.height*self.master.wc_ratio[1])

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
        return self.absolute_left + self.width*self.master.wc_ratio[0]

    @property
    def relative_bottom(self):
        """Return the bottom coordinate of the element in the frame."""
        return self.relative_top + self.height

    @property
    def absolute_bottom(self):
        """Return the bottom coordinate of the element in the game window."""
        return self.absolute_top + self.height*self.master.wc_ratio[1]

    @property
    def relative_left(self):
        """Return the left coordinate of the element in the frame."""
        return self._x - self.anchor[0]*self.width

    @property
    def absolute_left(self):
        """Return the left coordinate of the element in the game window."""
        return self.master.absolute_left + self.relative_left*self.master.wc_ratio[0]

    @property
    def relative_top(self):
        """Return the top coordinate of the element in the frame."""
        return self._y - self.anchor[1]*self.height

    @property
    def absolute_top(self):
        """Return the top coordinate of the element in the game window."""
        return self.master.absolute_top + self.relative_top*self.master.wc_ratio[1]
