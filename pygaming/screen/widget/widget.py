"""The widget module contains the widget class, which is a base for all widgets."""

from abc import ABC, abstractmethod
from ..frame import Frame
from typing import Optional
from pygame import Cursor, Surface, Rect
from ..element import Element, TOP_LEFT, SurfaceLike
from ..animated_surface import AnimatedSurface

def make_background(background: Optional[SurfaceLike], reference: AnimatedSurface):
    """
    Return an AnimatedSurface based on the inputs:
    If background is None, return a copy of the reference.
    If background is an animated surface, return it
    If background is a surface, create an animated surface with it.
    """
    if background is None:
        return reference.copy()
    elif isinstance(background, Surface):
        return AnimatedSurface([background], 4, 0)
    else:
        return background

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
        normal_background: SurfaceLike,
        focused_background: Optional[SurfaceLike] = None,
        disabled_background: Optional[SurfaceLike] = None,
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
        self.focused_background = make_background(focused_background, self.surface)
        self.disabled_background = make_background(disabled_background, self.surface)

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
        if not self._continue_animation:
            if self.disabled:
                self.disabled_background.update_animation(loop_duration)
            elif self.focused:
                self.focused_background.update_animation(loop_duration)
            else:
                self.normal_background.update_animation(loop_duration)
        else:
            self.disabled_background.update_animation(loop_duration)
            self.focused_background.update_animation(loop_duration)
            self.normal_background.update_animation(loop_duration)

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
