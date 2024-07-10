from typing import Any, Callable
from pygame import Cursor, Surface
import pygame
from pygaming.ui.inputs.inputs import Inputs
from pygaming.utils.color import Color, blue, cyan
from .slider import Slider, _make_slider_background, _DEFAULT_CURSOR_RADIUS, _DEFAULT_HEIGHT, _DEFAULT_WIDTH

class Switch(Slider):
    """An Switch is a 2-state slider."""

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
            transition_func: Callable[..., Any] = lambda x:x,
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
            return self._off_disable_bakcground.copy()
        elif self._focus:
            return self._off_focus_bakcground.copy()
        else:
            return self._off_background.copy()
    
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

    def update(self, inputs: Inputs, loop_duration: int, x_frame, y_frame):
        # Get if an arrow have been use or 
        if self._focus:
            arrows = inputs.get_arrows()
            if (pygame.KEYDOWN, pygame.K_RIGHT) in arrows:
                self.move_to_the_right()
            if (pygame.KEYDOWN, pygame.K_LEFT) in arrows:
                self.move_to_the_left()
            actions = inputs.get_actions()
            if "enter" in actions and actions["enter"] and self._focus:
                if self._value:
                    self.move_to_the_left()
                else:
                    self.move_to_the_right()

        # Get if the widget have been clicked
        clicks = self._update_mouse(inputs, x_frame, y_frame)
        if self._is_clicking and 1 in clicks:
            self._value = 1 - self._value
            self._current_transition = (1 - self._value, self._value)
            self._transition_delta = 0
        
        # Move the cursor during the transition
        if not (self._current_transition is None):
            if self._transition_duration != 0:
                self._transition_delta += loop_duration/self._transition_duration
            else:
                self._transition_delta = 1
            if self._transition_delta >= 1:
                self._transition_delta = 0
                self._current_transition = None
