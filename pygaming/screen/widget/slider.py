"""The Slider is Widget used to enter a numeric value within an interval."""
from typing import Optional, Iterable, Callable
from pygame import Cursor, Surface, Rect
from ..animated_surface import AnimatedSurface
from .widget import Widget, TOP_LEFT, make_background
from ..element import SurfaceLike
import pygame

class Slider(Widget):
    """The Slider is a widget that is used to select a value in a given range."""

    def __init__(
        self,
        master,
        x: int,
        y: int,
        values: Iterable,
        normal_background: SurfaceLike,
        normal_cursor: SurfaceLike,
        initial_value: Optional[int] = None,
        focused_background: Optional[SurfaceLike] = None,
        focused_cursor: Optional[SurfaceLike] = None,
        disabled_background:  Optional[SurfaceLike] = None,
        disabled_cursor:  Optional[SurfaceLike] = None,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Optional[Rect] = None,
        layer: int = 0,
        hover_surface: Surface | None = None,
        hover_cursor: Cursor | None = None,
        continue_animation: bool = False,
        transition_function: Callable[[float], float] = lambda x:x,
        transition_duration: int = 300, # [ms]
    ) -> None:
        super().__init__(
            master,
            x,
            y,
            normal_background,
            focused_background,
            disabled_background,
            anchor,
            active_area,
            layer,
            hover_surface,
            hover_cursor,
            continue_animation
        )

        self.normal_cursor = make_background(normal_cursor, None)
        self.focused_cursor = make_background(focused_cursor, self.normal_cursor)
        self.disabled_cursor = make_background(disabled_cursor, self.normal_cursor)

        # initial value and index
        self._values= list(values)
        self._index = min(range(len(self._values)), key=lambda i: abs(self._values[i] - initial_value))

        # the positions of the cursor for each value
        x_min = self._active_area.left + self.normal_cursor.width//2
        x_max = self._active_area.right - self.normal_cursor.width//2
        self._positions = [
              x_max*(t/(len(self._values)-1))
            + x_min*(1 - t/(len(self._values)-1))
            for t in range(len(self._values))
        ]

        self._absolute_active_area = self._active_area.move(self.absolute_x, self.absolute_y)
        self._cursor_width = self.normal_cursor.width
        self._holding_cursor = False

        # Transition-related attributes
        self._transition_func = transition_function
        self._transition_duration = transition_duration
        self._current_transition = None
        self._current_transition_delta = 0
        self._cursor_position = self._positions[self._index]

    def get(self):
        """Return the numeric value selected by the player."""
        return self._values[self._index]

    def update(self, loop_duration: int):
        """Update the slider based on the inputs."""

        # Get a click
        ck1 = self.game.mouse.get_click(1)


        # If the user is clicking:
        if ck1 is not None and self._absolute_active_area.collidepoint(ck1.x, ck1.y):
            local_x = ck1.x - self.absolute_left

            # If the user is clicking on the cursor, we want the cursor to follow the user click
            if self._cursor_position < local_x < self._cursor_position + self._cursor_width:
                self._holding_cursor = True

            # If the user is clicking elsewhere, we want the slider to set a transition to this position.
            elif not self._holding_cursor:

                # We verify that we clicked on a new position
                new_index = self._get_index_of_click(local_x)
                if new_index != self._index:
                    # In this case, we start a transition to it.
                    self._index = new_index
                    self._current_transition = (self._cursor_position, self._positions[self._index])
                    self._current_transition_delta = 0

            # In the case we are holding the cursor
            if self._holding_cursor: # We do not use else because we want to execute this after the 1st if.
                self._cursor_position = local_x

                self._index = self._get_index_of_click(local_x)

        # In the case the user is not clicking
        else:
            self._holding_cursor = False
            # if we are doing a transition
            if self._current_transition is not None:
                self._current_transition_delta += loop_duration/self._transition_duration
                t = self._transition_func(self._current_transition_delta)
                self._cursor_position = self._current_transition[0]*(1-t) + t*self._current_transition[1]

                # If we finished the transition
                if self._current_transition_delta > 1:
                    self._current_transition_delta = 0
                    self._current_transition = None
                    self._cursor_position = self._positions[self._index]

    def _get_index_of_click(self, x):
        """Get the index the closest to the click"""
        return min(range(len(self._positions)), key=lambda i: abs(self._positions[i] - x))

    def _get_normal_surface(self) -> Surface:
        background = self.normal_background
        cursor = self.normal_cursor
        return self._get_surface(background, cursor)

    def _get_focused_surface(self) -> Surface:
        background = self.focused_background
        cursor = self.focused_cursor
        return self._get_surface(background, cursor)

    def _get_disabled_surface(self) -> Surface:
        background = self.disabled_background
        cursor = self.disabled_cursor
        return self._get_surface(background, cursor)

    def _get_surface(self, background: AnimatedSurface, cursor: AnimatedSurface) -> Surface:
        """Make the surface with the cursor and the background."""
        bg = background.get()
        x = self._cursor_position - self.normal_cursor.width//2
        y = (background.height - cursor.height)//2
        bg.blit(cursor.get(), (x,y))
        return bg
