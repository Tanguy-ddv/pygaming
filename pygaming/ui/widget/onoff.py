from typing import Any, Callable
from pygame import Cursor, Surface
import pygame
from pygaming.utils.color import Color, blue, cyan
from .slider import Slider, _make_slider_background, _DEFAULT_CURSOR_RADIUS, _DEFAULT_HEIGHT, _DEFAULT_WIDTH

class OnOff(Slider):
    """An OnOff is a 2-state slider."""

    def __init__(
            self,
            frame,
            x: int,
            y: int,
            layer: int = 0,
            initial_value: bool = True,
            on_background: Surface | Color = blue,
            on_focus_background: Surface | Color | None = None,
            on_disable_background: Surface | Color | None = None,
            off_background: Surface | Color | None = None,
            off_focus_background: Surface | Color | None = None,
            off_disable_background: Surface | Color | None = None,
            width: int = _DEFAULT_WIDTH,
            height: int = _DEFAULT_HEIGHT,
            on_cursor: Surface | Color = cyan,
            off_cursor: Surface | Color = None,
            cursor_radius: int = _DEFAULT_CURSOR_RADIUS,
            margin_x: int = 10,
            margin_y: int = 5,
            transition_func: Callable[..., Any] = ...,
            transition_duration: float | int = 0,
            hover_cursor: Cursor | None = None
        ) -> None:
        Slider.__init__(
            self,
            frame,
            x,
            y,
            layer,
            lambda x:x,
            0,
            1,
            2,
            int(initial_value),
            on_background,
            on_focus_background,
            on_disable_background,
            width,
            height,
            on_cursor,
            cursor_radius,
            margin_x,
            margin_y,
            transition_func,
            transition_duration,
            hover_cursor
        )
        height = max(cursor_radius*2, height)
        self._off_background = _make_slider_background(off_background, width, height, self._background, margin_x, margin_y)
        self._off_focus_bakcground = _make_slider_background(off_focus_background, width, height, self._off_background, margin_x, margin_y)
        self._off_disable_bakcground = _make_slider_background(off_disable_background, width, height, self._disable_background, margin_x, margin_y)
        
        if isinstance(off_cursor, Color):
            self.off_cursor = pygame.Surface((2*cursor_radius, 2*cursor_radius), pygame.SRCALPHA)
            pygame.draw.circle(self.off_cursor, off_cursor.to_RGBA(), (cursor_radius, cursor_radius), cursor_radius)
        elif off_cursor is None:
            self.off_cursor = self.cursor.copy()
        else:
            self.off_cursor = pygame.transform.scale(off_cursor, (cursor_radius*2, cursor_radius*2))
        
    def _get_background(self) -> Surface:
        if self._value:
            return Slider._get_background(self)
        elif self._disabled:
            return self._off_disable_bakcground
        elif self._focus:
            return self._off_focus_bakcground
        else:
            return self._off_background
    
    def get_surface(self) -> Surface:
        background = self._get_background()
        
        y = (self.height - self.cursor.get_height())//2
        if self._current_transition is None:
            x = self._xes[self._value]
        else:
            # Source
            x_arr = self._xes[self._current_transition[1]]
            # Destination
            x_dep = self._xes[self._current_transition[0]]
            t = self._transition_func(self._transition_delta)
            x = t*x_arr + (1-t)*x_dep
        if self._value:
            background.blit(self.cursor, (x, y))
        else:
            background.blit(self.off_cursor, (x, y))
        return background
    
    def get(self) -> bool:
        return self._value == 1