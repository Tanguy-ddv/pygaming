"""The slider is a widget used to enter a numerical value."""

import pygame
from typing import Callable, Optional, Any

from pygaming.ui.inputs.inputs import Inputs
from ...io_.file import FontFile

from ...utils.color import Color, blue, cyan, white
from ...utils.text_flags import TextFlags
from .base_widget import BaseWidgetWithText

_DEFAULT_WIDTH = 150
_DEFAULT_CURSOR_RADIUS = 15
_DEFAULT_HEIGHT = 20

def _get_closest(x: float, xes: list[float], delta: float):
    """return the closest value"""
    return sorted(xes, key = lambda v: abs(x - (v + delta)))[0]

class Slider(BaseWidgetWithText):
    """A Slider widget is used to enter numerical value in the game."""

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        func: Callable[[float], Any] = lambda v: int(v) if int(v) == v else v,
        from_: float | int = 0,
        to : float | int = 4,
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
        display_value: bool = False,
        font_file: Optional[FontFile] = None,
        font_color: Color = white,
        font_size: int = 20,
        text_flags: TextFlags = TextFlags(),
        transition_func: Callable = lambda x: x,
        transition_duration: float | int = 0, # [ms]
        initial_focus: bool = False
    ) -> None:
        """
        A slider is a widget used to enter a value in the game.
        Params:
        ---
        frame: Frame. The frame in which the slider will be inserted.
        x:int, y:int. The position of the top-left corner on the frame.
        func: Callable. If not None, the return and the display are function of the value.
        from_: float, to: float. The first and last value of the numerical scale (before applying the function).
        nb_points: the number of points in the scale.
        initial_value: The initial value. if the value is not perfectly in the scale, set it to the immediate lower value possible.
        unfocus_background, focus_background: the background when the widget is on focus or not.
        If the provided background is a color, then create a rectangle of specified width and height with rounded extremities.
        If the provided background is a surface, is it as it is (possibly reshape it in shape (width, height)).
        If the focus_background is not None, use the unfocus_bakcground in both case.
        width: int, height: int. Dimension to shape/reshape the background.
        cursor: Color | Surface. The cursor that move on the scale. If a color is provided, make a circle of radius cursor_radius.
        If a surface is provided, use it as a cursor. Possibly reshape it a a shape (cursor_radius*2, cursor_radius*2) if it is not None.
        cursor_radius: int. Dimension To shape/reshape the cursor.
        margin_x: int, margin_x: int. The margin of the scale in its background.
        font_file: FontFile. The font file of the font used to display the text of the value. Optional if value_display_position is False
        display_value: bool. if True, display the value on the cursor. If you want to display it elsewhere, use a label widget.
        font_color: Color. the color of the font.
        font_size: int. the size of the font.
        text_flags: TextFlags. flags for the text.
        transition_func: Callable. A function [0,1] -> R with f(0) = 0 and f(1) = 1 that represent the path from one position to another.
        transition_duration: int (ms). The duration of the transition in ms.
        initial_focus: bool. If false, you have to click to set the focus on the entry before interacting with.        
        """

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
            width = bg.get_width() - 2*margin_x
            height = bg.get_height() - 2*margin_y
            focus_bg = create_background(width, focus_background)
        elif focus_background is None:
            focus_bg = bg.copy()
        else:
            focus_bg = focus_background.copy()

        super().__init__(frame, x, y, bg.get_width(), self.height, bg, focus_bg, font_color, text_flags, font_file, font_size, initial_focus)

        self._from = from_
        self._to = to
        self._nb_points = nb_points
        self._func = lambda v: func(v*(self._to - self._from)/(self._nb_points-1) + self._from)

        # Set the initial value
        if initial_value is None:
            initial_value = from_

        if initial_value > to:
            initial_value = to

        self._value = int((initial_value - from_)/(to - from_)*self._nb_points)
        if self._value == self._nb_points:
            self._value -= 1

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

        self.margin_y = margin_y
        self._display_value = display_value

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
    
    def update(self, inputs: Inputs, loop_duration: int, x_frame, y_frame):
        """Update the slider with a click or by moving an object."""
        # Get if an arrow have been pressed.
        if self._focus:
            arrows = inputs.get_arrows()
            if (pygame.KEYDOWN, pygame.K_RIGHT) in arrows:
                self._move_to_the_right()
            if (pygame.KEYDOWN, pygame.K_LEFT) in arrows:
                self._move_to_the_left()
            # Get if a position have been clicked
            clicks = inputs.get_clicks(x_frame, y_frame)
            if 1 in clicks and not clicks[1].up:
                click = clicks[1]
                if self.y + self.margin_y < click.y < self.y + self.height - self.margin_y and self.x < click.x < click.x + self.width:
                    # The click is on the widget
                    previous_value = self._value
                    closest_x = _get_closest(click.x - self.x, self._xes, self.cursor.get_width()//2)
                    new_value = self._xes.index(closest_x)
                    if 0 <= new_value <= self._nb_points - 1:
                        self._value = new_value
                        self._current_transition = (previous_value, self._value)
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
        if self._display_value:
            text = self._render(str(self.get()))
            background.blit(text, (x - text.get_width()//2 + self.cursor.get_width()//2, y - text.get_height()//2 + self.cursor.get_height()//2))
        return background