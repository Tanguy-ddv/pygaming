"""The widget module contains the widget class, which is a base for all widgets."""

from abc import ABC, abstractmethod
from typing import Optional
from pygame import Cursor, Surface
from ..element import Element, TOP_LEFT, SurfaceLike
from ..animated_surface import AnimatedSurface

class Widget(Element, ABC):
    """
    Widget is an abstract class for all the widgets. They are all element able to get information from the player.
    Every widget must have the get method to return the input, the _get_normal_surface, _get_focused_surface and _get_disable_surface
    to return the surface in the three cases, and an update method to update the widget.
    """

    def __init__(
        self,
        master,
        x: int,
        y: int,
        background: SurfaceLike,
        focused_background: Optional[SurfaceLike] = None,
        disabled_background: Optional[SurfaceLike] = None,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        layer: int = 0,
        hover_surface: Surface | None = None,
        hover_cursor: Cursor | None = None) -> None:
        super().__init__(
            master,
            background,
            x,
            y,
            anchor,
            layer,
            hover_surface,
            hover_cursor,
            True,
            True
        )
        if focused_background is None:
            focused_background = self.surface.copy()
        if isinstance(focused_background, Surface):
            self.focused_background = AnimatedSurface([focused_background], 4, 0)
        else:
            self.focused_background = focused_background

        if disabled_background is None:
            disabled_background = self.surface.copy()
        if isinstance(disabled_background, Surface):
            self.disabled_background = AnimatedSurface([disabled_background], 4, 0)
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
    def _get_normal_surface(self) -> Surface:
        """Return the surface based on its current state when the widget it is neither focused nor disabled."""
        raise NotImplementedError()

    @abstractmethod
    def _get_focused_surface(self) -> Surface:
        """Return the surface based on its current state when the widget is focused."""
        raise NotImplementedError()

    @abstractmethod
    def _get_disabled_surface(self) -> Surface:
        """Return the surface based on its current state when the widget is disabled."""
        raise NotImplementedError()

    def get_surface(self):
        """Return the surface of the widget."""
        if self.disabled:
            return self._get_disabled_surface()
        elif self.focused:
            return self._get_focused_surface()
        else:
            return self._get_normal_surface()

    def loop(self, loop_duration: int):
        """Call this method every loop iteration."""
        if self.disabled:
            self.disabled_background.update_animation(loop_duration)
        elif self.focused:
            self.focused_background.update_animation(loop_duration)
        else:
            self.normal_background.update_animation(loop_duration)
        
        self.update(loop_duration)

    def switch_background(self):
        """Switch to the disabled, focused or normal background."""
        if self.disabled:
            self.focused_background.reset()
            self.normal_background.reset()
        elif self.focused:
            self.normal_background.reset()
            self.disabled_background.reset()
        else:
            self.disabled_background.reset()
            self.focused_background.reset()
