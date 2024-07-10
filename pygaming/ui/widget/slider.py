"""The slider is a widget used to enter a numerical value."""

import pygame
from typing import Callable, Optional, Any

from pygaming.ui.inputs.inputs import Inputs
from ...io_.file import FontFile, default_font
from ..utils import make_rounded_rectangle

from ...utils.color import Color, blue, cyan, white
from .base_widget import BaseWidget
from .supports import MouseInteractionSupport, TextSupport, DisableSupport, FocusSupport

_DEFAULT_WIDTH = 200
_DEFAULT_CURSOR_RADIUS = 15
_DEFAULT_HEIGHT = 40

def _get_closest(x: float, xes: list[float], delta: float):
    """return the closest value"""
    return sorted(xes, key = lambda v: abs(x - (v + delta)))[0]

def _make_slider_background(background: Color | pygame.Surface | None, width: int, height: int, reference: pygame.Surface | None, margin_x: int, margin_y: int):
    """Make the background of a slider."""
    if isinstance(background, pygame.Surface):
        bg = pygame.transform.scale(background, (width, height))
    elif background is None:
        bg = reference.copy()
    else:
        rounded_rect = make_rounded_rectangle(background, width - 2*margin_x, height - 2*margin_y)
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.blit(rounded_rect, (margin_x, margin_y))
    return bg

class Slider(BaseWidget, MouseInteractionSupport, DisableSupport, FocusSupport):
    """A Slider widget is used to enter numerical value in the game."""

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        layer: int = 0,
        func: Callable[[float], Any] = lambda v: int(v) if int(v) == v else v,
        from_: float | int = 0,
        to : float | int = 4,
        nb_points: int = 5,
        initial_value: Optional[float | int] = None,
        background: pygame.Surface | Color = blue,
        focus_background: Optional[pygame.Surface | Color] = None,
        disable_background: Optional[pygame.Surface | Color] = None,
        width: int = _DEFAULT_WIDTH,
        height: int = _DEFAULT_HEIGHT,
        cursor: pygame.Surface | Color = cyan,
        cursor_radius: int = _DEFAULT_CURSOR_RADIUS,
        margin_x: int = 10,
        margin_y: int = 5,
        transition_func: Callable = lambda x: x,
        transition_duration: float | int = 0, # [ms]
        hover_cursor: pygame.Cursor | None = None,
    ) -> None:
        """
        A slider is a widget used to enter a value in the game.
        Params:
        ---
        frame: Frame. The frame in which the slider will be inserted.
        x:int, y:int. The position of the top-left corner on the frame.
        layer: the layer of the object in the frame.
        func: Callable. If not None, the return and the display are function of the value.
        from_: float, to: float. The first and last value of the numerical scale (before applying the function).
        nb_points: the number of points in the scale.
        initial_value: The initial value. if the value is not perfectly in the scale, set it to the immediate lower value possible.
        background: the background of the widget, if it is a color, create a rectangle with rounded edges
        of shape (width - 2*margin_x, height - 2*margin_y) on a transparent background.
        focus_background: The background of the widget if it is focused. If it is color, create a rectangle with rounded edges
        of shape (width - 2*margin_x, height - 2*margin_y) on a transparent background. if it is None, use the main background.
        disable_background: The background of the widget if it is focused. If it is color, create a rectangle with rounded edges
        of shape (width - 2*margin_x, height - 2*margin_y) on a transparent background. if it is None, use the main background.
        cursor: If it is a Surface, use it as the cursor of the slider. If it is a color, create a circle of that color.
        cursor_radius: int. Dimension To shape/reshape the cursor.
        margin_x: int, margin_y: int. The margin of the scale in its background for the creation of a rounded rectangle.
        transition_func: Callable. A function [0,1] -> R with f(0) = 0 and f(1) = 1 that represent the path from one position to another.
        transition_duration: int (ms). The duration of the transition in ms.
        hover_cursor: The image of the mouse when it is above the widget.
        """

        # If the cursor is a color, create a circle of that color.
        if isinstance(cursor, Color):
            self.cursor = pygame.Surface((2*cursor_radius, 2*cursor_radius), pygame.SRCALPHA)
            pygame.draw.circle(self.cursor, cursor.to_RGBA(), (cursor_radius, cursor_radius), cursor_radius)
        else:
            self.cursor = pygame.transform.scale(cursor, (cursor_radius*2, cursor_radius*2))
        height = max(cursor_radius*2, height)

        bg = _make_slider_background(background, width, height, None, margin_x, margin_y)
        focus_bg = _make_slider_background(focus_background, width, height, bg, margin_x, margin_y)
        disable_bg = _make_slider_background(disable_background, width, height, bg, margin_x, margin_y)

        BaseWidget.__init__(self, frame, x, y, layer)
        FocusSupport.__init__(self, bg, focus_bg)
        MouseInteractionSupport.__init__(self, bg, x, y, layer, hover_cursor)
        DisableSupport.__init__(self, bg, disable_bg)

        self._from = from_
        self._to = to
        self._nb_points = nb_points
        self._func = lambda v: func(v*(self._to - self._from)/(self._nb_points-1) + self._from)

        # Set the initial value
        if initial_value is None:
            initial_value = from_

        if initial_value > to:
            initial_value = to

        self._value = int((initial_value - from_)/(to - from_)*(self._nb_points-1))
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

    def get(self):
        """Return the value of the slider."""
        return self._func(self._value)

    def move_to_the_right(self):
        """Move the cursor to the right."""
        if self._value < self._nb_points - 1:
            self._value += 1
            self._transition_delta = 0
            self._current_transition = (self._value - 1, self._value)
    
    def move_to_the_left(self):
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
                self.move_to_the_right()
            if (pygame.KEYDOWN, pygame.K_LEFT) in arrows:
                self.move_to_the_left()
        
        # Get if a position have been clicked
        clicks = self._update_mouse(inputs, x_frame, y_frame)
        if self._is_clicking and 1 in clicks:
            click = clicks[1]
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

        background.blit(self.cursor, (x, y))
        return background

class TextSlider(Slider, TextSupport):
    """A text slider is a slider that display its value on its cursor."""

    def __init__(
        self,
        frame, 
        x: int, 
        y: int, 
        layer: int = 0, 
        func: Callable[[float], Any] = lambda v: int(v) if int(v) == v else v, 
        from_: float | int = 0, 
        to: float | int = 4, 
        nb_points: int = 5, 
        initial_value: float | int | None = None, 
        background: pygame.Surface | Color = blue, 
        focus_background: pygame.Surface | Color | None = None, 
        disable_background: pygame.Surface | Color | None = None, 
        width: int = _DEFAULT_WIDTH, 
        height: int = _DEFAULT_HEIGHT, 
        cursor: pygame.Surface | Color = cyan, 
        cursor_radius: int = _DEFAULT_CURSOR_RADIUS, 
        margin_x: int = 10, 
        margin_y: int = 5, 
        font_file: FontFile = default_font, 
        font_color: Color = white, 
        font_size: int = 20, 
        italic: bool = False, 
        bold: bool = False, 
        underline: bool = False, 
        antialias: bool = True, 
        transition_func: Callable[..., Any] = lambda x: x,
        transition_duration: float | int = 0, 
        hover_cursor: pygame.Cursor | None = None
    ) -> None:
        
        """
        A text slider is a widget used to enter a value in the game.
        unlike a simple slider, it displays the value on the cursor.
        Params:
        ---
        frame: Frame. The frame in which the slider will be inserted.
        x:int, y:int. The position of the top-left corner on the frame.
        layer: the layer of the object in the frame.
        func: Callable. If not None, the return and the display are function of the value.
        from_: float, to: float. The first and last value of the numerical scale (before applying the function).
        nb_points: the number of points in the scale.
        initial_value: The initial value. if the value is not perfectly in the scale, set it to the immediate lower value possible.
        background: the background of the widget, if it is a color, create a rectangle with rounded edges
        of shape (width - 2*margin_x, height - 2*margin_y) on a transparent background.
        focus_background: The background of the widget if it is focused. If it is color, create a rectangle with rounded edges
        of shape (width - 2*margin_x, height - 2*margin_y) on a transparent background. if it is None, use the main background.
        disable_background: The background of the widget if it is focused. If it is color, create a rectangle with rounded edges
        of shape (width - 2*margin_x, height - 2*margin_y) on a transparent background. if it is None, use the main background.
        cursor: If it is a Surface, use it as the cursor of the slider. If it is a color, create a circle of that color.
        cursor_radius: int. Dimension To shape/reshape the cursor.
        margin_x: int, margin_y: int. The margin of the scale in its background for the creation of a rounded rectangle.
        font_file: FontFile the fontFile that represent the font you want to use.
        font_color: Color the color of the font.
        font_size: the size of the font, 
        italic, bold, underline, antialias: flags for the text. 
        transition_func: Callable. A function [0,1] -> R with f(0) = 0 and f(1) = 1 that represent the path from one position to another.
        transition_duration: int (ms). The duration of the transition in ms.
        hover_cursor: The image of the mouse when it is above the widget.
        """
        Slider.__init__(
            self,
            frame=frame, 
            x=x, 
            y=y, 
            layer=layer, 
            func=func, 
            from_=from_, 
            to=to, 
            nb_points=nb_points, 
            initial_value=initial_value, 
            background=background, 
            focus_background=focus_background, 
            disable_background=disable_background, 
            width=width, 
            height=height, 
            cursor=cursor, 
            cursor_radius=cursor_radius, 
            margin_x=margin_x, 
            margin_y=margin_y, 
            transition_func=transition_func,
            transition_duration=transition_duration,
            hover_cursor=hover_cursor,
        )
        TextSupport.__init__(self, font_color,font_file, font_size, italic, bold, underline, antialias)

    def get_surface(self):
        """Construct the surface."""
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

        background.blit(self.cursor, (x, y))

        text = self._render(str(self.get()))
        background.blit(text, (x - text.get_width()//2 + self.cursor.get_width()//2, y - text.get_height()//2 + self.cursor.get_height()//2))
        return background