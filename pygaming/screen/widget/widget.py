"""The widget module contains the widget class, which is a base for all widgets."""

from abc import ABC, abstractmethod
from ..frame import Frame
from typing import Optional
from pygame import Cursor, Surface, Rect
from ..element import Element, TOP_LEFT
from ..art.art import Art

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
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Optional[Rect] = None,
        layer: int = 0,
        hover_surface: Surface | None = None,
        hover_cursor: Cursor | None = None,
        continue_animation: bool = False
    ) -> None:
        super().__init__(
            master,
            normal_background,
            x,
            y,
            anchor,
            layer,
            hover_surface,
            hover_cursor,
            True,
            True
        )
        if active_area is None:
            active_area = self.surface.get().get_rect()
        self._active_area = active_area
        self._absolute_active_area = self._active_area.move(self.absolute_left, self.absolute_top)
        self._continue_animation = continue_animation
        if focused_background is None:
            self.focused_background = self.surface
        else:
            self.focused_background = focused_background

        if disabled_background is None:
            self.disabled_background = self.surface
        else:
            self.disabled_background = disabled_background

    @property
    def normal_background(self):
        """Alias for the surface."""
        return self.surface

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
        self.normal_background.start()
        self.focused_background.start()
        self.disabled_background.start()

    def end(self):
        """Execute this method at the end of the phase, unload all the arts."""
        self.normal_background.unload()
        self.focused_background.unload()
        self.disabled_background.unload()
