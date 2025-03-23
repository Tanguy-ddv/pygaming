"""the element module contains the Element object, which is a base for every object displayed on the game window."""
from __future__ import annotations
from abc import abstractmethod
from typing import Optional
import pygame
from ._master import Master
from .tooltip import Tooltip
from .art.art import Art
from .anchors import TOP_LEFT, Anchor, AnchorLike, CENTER_CENTER
from ..inputs import Click
from ..cursor import Cursor
from ._visual import Visual
from .hitbox import Hitbox
from ..error import PygamingException

class Element(Visual):
    """Element is the abstract class for everything object displayed on the game window: widgets, actors, frames."""

    def __init__(
        self,
        master: Master,
        background: Art,
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

        Visual.__init__(self, background, update_if_invisible)
        self.visible = True
        self.can_be_focused = can_be_focused
        self.focused = False
        self.can_be_disabled = can_be_disabled
        self.disabled = False

        if active_area is None:
            active_area = Hitbox(0, 0, *self.background.size)
        self._active_area = active_area

        self._x = None
        self._y = None
        self.anchor = None
        self.layer = None
        self.master = master
        self.master.add_child(self)
        self.on_master = False

        self._cursor = cursor
        self._tooltip = tooltip

        self._current_grid = None # None or a Grid.

    def get_on_master(self):
        """Reassign the on_screen argument to whether the object is inside the screen or outside."""
        on_screen = self.absolute_rect.colliderect((0, 0, *self.game.config.dimension))
        self.on_master = on_screen and self.master.is_child_on_me(self)

    def place(self, x: int, y: int, anchor: AnchorLike = TOP_LEFT, layer=0):
        """
        Place the element on its master.
        
        :param x: int, the horizontal coordinate in the master, of the anchor.
        :param y: int, the vertical coordinate in the master, of the anchor.
        :param anchor: Anchor, the anchor point of the element that will be placed at the coordinate (x,y)
        :param layer: int, the z-coordinate of the element, used to manage the order of display and interaction.

        :return self: Element, the element itself is returned allowing method chaining.
        """

        # Remove the element from the node.
        if self._current_grid is not None:
            self._current_grid.remove(self)
            self._current_grid = None

        self._x = x
        self._y = y
        self.anchor = Anchor(anchor)
        self.layer = layer

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()
        
        return self

    def grid(self,
        row: int,
        column: int,
        grid = None,
        rowspan: int = 1,
        columnspan: int = 1,
        padx: int = 0,
        pady: int = 0,
        anchor: AnchorLike = TOP_LEFT,
        justify: AnchorLike = CENTER_CENTER,
        layer: int = 0
    ) -> Element:
        """
        Place the element on its master using a grid.
        
        :param row: int, The row on the grid this element is placed on.
        :param column: int, The column on the grid this element is placed on.
        :param grid: int = None, Grid or None. If None, then the first grid is used. If an int is provided, the grid-th grid of the master is used.
            If the master do not have a grid-th Grid, then it is created with an anchor of TOP_LEFT and coordinates of 0, 0.
            If a Grid is provided (an object created by master.create_grid(...)), then it is used.
        :param rowspan: int = 1 the number of row the element can span across
        :param: columnspan: int = 1 the number of columns the element can span across
        :param padx: int = 0 the number of pixels added on the left and right of the element
        :param pady: int = 0 the number of pixels added above and below the element
        :param anchor: Anchor = TOP_LEFT, the anchor of the element.
        :param justify: Anchor = CENTER. In case the cell is larger than the element, this is used to specify where the element should be aligned
        :param layer: int, the z-coordinate of the element, used to manage the order of display and interaction.

        :return self: Element, the element itself is returned allowing method chaining.
        """

        if self._current_grid is not None:
            self._current_grid.remove(self)

        grid = self.master.get_grid(grid)
        self.anchor = Anchor(anchor)
        grid.add(row, column, self, rowspan, columnspan, padx, pady, self.anchor , Anchor(justify))
        self._current_grid = grid
        self._x, self._y = grid.get(row, column)
        self.layer = layer

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()

        return self

    def move(self, dx: int = 0, dy: int = 0):
        """
        Move the element on its master.
        
        Params:
        ---
        - dx: int = 0, the number of pixel by which the element should be translated horizontally
        - dy: int = 0, the number of pixel by which the element should be translated vertically

        Note:
        ----
        If the element has been placed with grid, it is removed from the grid.
        """

        if self._current_grid is not None:
            self._current_grid.remove(self)
            self._current_grid = None

        if self._x is None:
            raise PygamingException(f"{self} cannot be move as it has not been placed yet.")

        self._x += dx
        self._y += dy

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()

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
            Visual.loop(self, loop_duration)
            self.update(loop_duration)

    def begin(self):
        """
        Execute this method at the beginning of the phase
        to load the active area and the background before running class-specific start method.
        """
        self._active_area.load(self.game.settings)
        Visual.begin(self, self.game.settings)
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
        Visual.finish(self)
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
