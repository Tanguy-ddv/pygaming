"""The widget module contains the widget class, which is a base for all widgets."""

from abc import ABC, abstractmethod
from typing import Optional
from pygame import Surface
from ..frame import Frame
from ..element import Element
from ..anchors import TOP_LEFT, Anchor
from ..art import Art
from ...cursor import Cursor
from ..tooltip import Tooltip
from ..hitbox import Hitbox

class Widget(Element, ABC):
    """
    Widget is an abstract class for all the widgets. They are all element able to get information from the player.
    Every widget must have the get method to return the input, the _get_normal_surface, _get_focused_surface and _get_disable_surface
    to return the surface in the three cases, and an update method to update the widget.
    """

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: Art,
        focused_background: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        anchor: Anchor = TOP_LEFT,
        active_area: Optional[Hitbox] = None,
        layer: int = 0,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        update_if_invisible: bool = False
    ) -> None:
        super().__init__(
            master,
            normal_background,
            x,
            y,
            anchor,
            layer,
            tooltip,
            cursor,
            True,
            True,
            active_area,
            update_if_invisible
        )
        self._continue_animation = continue_animation
        if focused_background is None:
            self.focused_background = self.background
        else:
            self.focused_background = focused_background

        if disabled_background is None:
            self.disabled_background = self.background
        else:
            self.disabled_background = disabled_background

    @property
    def normal_background(self):
        """Alias for the surface."""
        return self.background

    @abstractmethod
    def get(self):
        """Return the value of the widget input."""
        raise NotImplementedError()

    @abstractmethod
    def _make_normal_surface(self) -> Surface:
        """Return the surface based on its current state when the widget it is neither focused nor disabled."""
        raise NotImplementedError()

    @abstractmethod
    def _make_focused_surface(self) -> Surface:
        """Return the surface based on its current state when the widget is focused."""
        raise NotImplementedError()

    @abstractmethod
    def _make_disabled_surface(self) -> Surface:
        """Return the surface based on its current state when the widget is disabled."""
        raise NotImplementedError()

    def make_surface(self):
        """Return the surface of the widget."""
        if self.disabled:
            return self._make_disabled_surface()
        elif self.focused:
            return self._make_focused_surface()
        else:
            return self._make_normal_surface()

    def loop(self, loop_duration: int):
        """Call this method every loop iteration."""
        if not self._continue_animation:
            if self.disabled:
                has_changed = self.disabled_background.update(loop_duration)
            elif self.focused:
                has_changed = self.focused_background.update(loop_duration)
            else:
                has_changed = self.normal_background.update(loop_duration)
            if has_changed:
                self.notify_change()
        else:
            has_changed = self.normal_background.update(loop_duration)
            if has_changed:
                self.notify_change()
        if self.is_visible():
            self.update(loop_duration)

    def switch_background(self):
        """Switch to the disabled, focused or normal background."""
        if not self._continue_animation:
            if self.disabled:
                self.focused_background.reset()
                self.normal_background.reset()
            elif self.focused:
                self.normal_background.reset()
                self.disabled_background.reset()
            else:
                self.disabled_background.reset()
                self.focused_background.reset()

        self.notify_change()

    def start(self):
        """Execute this method at the beginning of the phase, load the arts that are set to force_load."""
        self.normal_background.start(**self.game.settings)
        self.focused_background.start(**self.game.settings)
        self.disabled_background.start(**self.game.settings)

    def end(self):
        """Execute this method at the end of the phase, unload all the arts."""
        self.normal_background.end()
        self.focused_background.end()
        self.disabled_background.end()
