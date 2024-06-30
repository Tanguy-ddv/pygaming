"""The slider is a widget used to enter a numerical value."""

import pygame
from typing import Callable, Optional, Any

from pygaming.ui.inputs.inputs import Inputs
from ...io_.file import FontFile

from ...utils.color import Color, blue, cyan, white
from .base_widget import BaseWidget

_DEFAULT_WIDTH = 50
_DEFAULT_CURSOR_RADIUS = 15
_DEFAULT_HEIGHT = 20

def _get_closest(x: float, xes: list[float], delta: float):
    """return the closest value"""
    return sorted(xes, key = lambda v: abs(x - (v + delta)))[0]

class Slider(BaseWidget):
    """A Slider widget is used to enter numerical value in the game."""

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        font_file: FontFile,
        func: Optional[Callable[[float], Any]] = None,
        from_: float | int = 0,
        to : float | int = 100,
        nb_points: int = 5,
        initial_value: Optional[float | int] = None,
        unfocus_background: pygame.Surface | Color = blue,
        focus_background: Optional[pygame.Surface | Color] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        cursor: pygame.Surface | Color = cyan,
        cursor_radius: Optional[int] = None,
        margin_x: int = 10,
        margin_y: int = 5,
        font_color: Color = white,
        font_size: int = 20,
        bold: bool = False,
        underline: bool = False,
        italic: bool = False,
        antialias: bool = True,
        transition_func: Callable = lambda x: x,
        transition_duration: float | int = 0, # [ms]
        initial_focus: bool = False
    ) -> None:

        self._font_color = font_color
        self._antialias = antialias
        self._font = font_file.get(font_size, italic, bold, underline)

        # If the cursor is a color, create a circle of that color.
        if isinstance(cursor, Color):
            if cursor_radius is None:
                cursor_radius = _DEFAULT_CURSOR_RADIUS
            self.cursor = pygame.Surface((2*cursor_radius, 2*cursor_radius), pygame.SRCALPHA)
            pygame.draw.circle(self.cursor, cursor.to_RGBA(), (cursor_radius, cursor_radius), cursor_radius)
        elif cursor_radius is None:
            self.cursor = cursor.copy()
            cursor_radius = self.cursor.get_height()//2
        else:
            self.cursor = pygame.transform.scale(cursor, (cursor_radius*2, cursor_radius*2))
        if height is not None:
            self.height = max(self.cursor.get_height(), height) + 2*margin_y
        else:
            self.height = self.cursor.get_height() + 2*margin_y

        def create_background(width, color: Color):
            bg = pygame.Surface((width  + 2*margin_x, self.height), pygame.SRCALPHA)
            # Create a rectangle with rounded corners.
            rect_left = margin_x + height//2
            rect_right = bg.get_width() - margin_x - height//2
            rect = pygame.rect.Rect(rect_left, (self.height - height)//2, rect_right - rect_left, height)
            pygame.draw.rect(bg, color.to_RGBA(), rect)
            pygame.draw.circle(bg, color.to_RGBA(), (rect_left, self.height//2), height//2)
            pygame.draw.circle(bg, color.to_RGBA(), (rect_right, self.height//2), height//2)
            return bg

        # If the background is a color, create a colored bar of that color on a transparent background
        if isinstance(unfocus_background, Color):
            if width is None:
                width = _DEFAULT_WIDTH
            if height is None:
                height = _DEFAULT_HEIGHT
            bg = create_background(width, unfocus_background)
        else:
            bg = unfocus_background.copy()
        
        if isinstance(focus_background, Color):
            if width is None:
                width = _DEFAULT_WIDTH
            if height is None:
                height = _DEFAULT_HEIGHT
            focus_bg = create_background(width, focus_background)
        elif focus_background is None:
            focus_bg = bg.copy()
        else:
            focus_bg = focus_background.copy()

        super().__init__(frame, x, y, bg.get_width(), self.height, bg, focus_bg, initial_focus)

        self._from = from_
        self._to = to
        self._nb_points = nb_points
        if func is None:
            func = lambda v: v
        self._func = lambda v: func(v*(self._to - self._from)/self._nb_points + self._from)

        # Set the initial value
        if initial_value is None:
            initial_value = from_

        if initial_value > to:
            initial_value = to

        self._value = int((initial_value - from_)/(to - from_)*self._nb_points)

        # The transitions params
        self._transition_func = transition_func
        self._transition_duration = transition_duration
        self._transition_delta = 0
        self._current_transition = None
        self._distance_between_two_stops = width//(self._nb_points-1)

        self._x_min = self.cursor.get_width()//2 + margin_x
        self._x_max = self.width - self.cursor.get_width()//2 - margin_x

        self._xes = [
            self._x_min + (self._x_max - self._x_min)/(self._nb_points-1)*value - self.cursor.get_width()//2
            for value in range(self._nb_points)
        ]

    def get(self):
        """Return the value of the slider."""
        return self._func(self._value)

    def _move_to_the_right(self):
        """Move the cursor to the right."""
        if self._value < self._nb_points - 1:
            self._value += 1
            self._transition_delta = 0
            self._current_transition = (self._value - 1, self._value)
    
    def _move_to_the_left(self):
        """Move the cursor to the left."""
        if self._value > 0:
            self._value -= 1
            self._current_transition = (self._value + 1, self._value)
    
    def update(self, inputs: Inputs, loop_duration: int):
        """Update the slider with a click or by moving an object."""
        # Get if an arrow have been pressed.
        if self._focus:
            arrows = inputs.get_arrows()
            if (pygame.KEYDOWN, pygame.K_RIGHT) in arrows:
                self._move_to_the_right()
            if (pygame.KEYDOWN, pygame.K_LEFT) in arrows:
                self._move_to_the_left()
            # Get if a position have been clicked
            clicks = inputs.get_clicks()
            if 1 in clicks and not clicks[1].up:
                x = clicks[1].x
                y = clicks[1].y
                if self.y < y < self.y + self.height:
                    # The click is on the widget
                    previous_value = self._value
                    closest_x = _get_closest(x - self.x, self._xes, self.cursor.get_width()//2)
                    new_value = self._xes.index(closest_x)
                    if 0 <= new_value <= self._nb_points - 1:
                        self._value = new_value
                        self._current_transition = (previous_value, self._value)
                        self._transition_delta = 0

        # Move the cursor during the transition
        if not (self._current_transition is None):
            self._transition_delta += loop_duration/self._transition_duration
            if self._transition_delta > 1:
                self._transition_delta = 0
                self._current_transition = None
    
    def get_surface(self) -> pygame.Surface:
        """Construct the surface."""
        if self._focus:
            background = self.focus_background.copy()
        else:
            background = self.unfocus_background.copy()

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

        background.blit(self.cursor, (x, y))
        text = self._font.render(str(self._value), self._antialias, self._font_color.to_RGBA())
        background.blit(text, (x+2, y))
        return background