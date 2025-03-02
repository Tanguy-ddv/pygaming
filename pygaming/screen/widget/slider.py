"""The Slider is Widget used to enter a numeric value within an interval."""
from typing import Optional, Iterable, Any
from pygame import Surface
from ZOCallable import ZOCallable, verify_ZOCallable
from ZOCallable.functions import linear
from ...error import PygamingException
from .widget import Widget
from ..anchors import TOP_LEFT, Anchor
from ..frame import Frame
from ..art.art import Art
from ...cursor import Cursor
from ..tooltip import Tooltip
from ..hitbox import Hitbox

class Slider(Widget):
    """The Slider is a widget that is used to select a value in a given range."""

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        values: Iterable,
        normal_background: Art,
        normal_cursor: Art,
        initial_value: Optional[Any] = None,
        focused_background: Optional[Art] = None,
        focused_cursor: Optional[Art] = None,
        disabled_background:  Optional[Art] = None,
        disabled_cursor:  Optional[Art] = None,
        anchor: Anchor = TOP_LEFT,
        active_area: Optional[Hitbox] = None,
        layer: int = 0,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        transition_function: ZOCallable = linear,
        transition_duration: int = 300, # [ms]
        update_if_invisible: bool = True,
        step_wth_arrow: int = 1,
    ) -> None:
        """
        A Slider is a widget that is used to select a value in a given range by moving a cursor from left to right on a background.

        Params:
        ---
        - master: Frame. The Frame in which this widget is placed.
        - x: int, the coordinate of the anchor in the master Frame
        - y: int, the top coordinate of the anchor in the master Frame.
        - values: Iterable, the ordered list of values from which the slider can select.
        - normal_background: AnimatedSurface | Surface: The surface used as the background of the slider when it is neither focused nor disabled.
        - normal_cursor: AnimatedSurface | Surface: The surface used as the cursor of the slider when it is neither focused nor disabled.
        - initial_value: Any, The initial value set to the cursor. If None, use the first value.
        - focused_background: AnimatedSurface | Surface: The surface used as the background of the slider when it is focused.
        - focused_cursor: AnimatedSurface | Surface: The surface used as the cursor of the slider when it is focused.
        - disabled_background: AnimatedSurface | Surface: The surface used as the background of the slider when it is disabled.
        - disabled_cursor: AnimatedSurface | Surface: The surface used as the cursor of the slider when it is disabled.
        - anchor: tuple[float, float]. The point of the slider that is placed at the coordinate (x,y).
          Use TOP_LEFT, TOP_RIGHT, CENTER, BOTTOM_LEFT or BOTTOM_RIGHT, or another personized tuple.
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the slider. if None, then it is the whole background.
        - layer: int, the layer of the slider in its master frame
        - tooltip: Tooltip, the tooltip to show when the slider is hovered.
        - cursor: Cursor The cursor of the mouse to use when the widget is hovered
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - transition_function: func [0, 1] -> [0, 1] A function that represent the position of the cursor during a transition given the transition duration.
            Default is lambda x:x. For an accelerating transition, use lambda x:x**2, for a decelerating transition, lambda x:x**(1/2), or other.
            Conditions: transition_function(0) = 0, transition_function(1) = 1
        - transition_duration: int [ms], the duration of the transition in ms.
        - update_if_invisible: bool, set to True if you want the widget to be update even if it is not visible. Default is True to finish the transitions.
        - step_wth_arrow: int, the number of step the slider should do when it is updated with an arrow of the keyboard. Default is 1
        """
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
            tooltip,
            cursor,
            continue_animation,
            update_if_invisible
        )

        self.normal_cursor = normal_cursor
        self.focused_cursor = focused_cursor if focused_cursor else normal_cursor
        self.disabled_cursor = disabled_cursor if disabled_cursor else normal_cursor

        # initial value and index
        self._values= list(values)
        self._initial_value = initial_value
        self._index = 0

        self._positions = []

        self._cursor_width = self.normal_cursor.width
        self._holding_cursor = False

        # Transition-related attributes
        verify_ZOCallable(transition_function)
        self._transition_func = transition_function
        self._transition_duration = transition_duration
        self._current_transition = None
        self._current_transition_delta = 0
        self._cursor_position = None

        self._step_wth_arrow = step_wth_arrow

    def get(self):
        """Return the value selected by the player."""
        return self._values[self._index]

    def start(self):
        # the positions of the cursor for each value
        self.normal_background.set_load_on_start()
        super().start()
        if self._initial_value is None:
            self._index = 0
        elif self._initial_value in self._values:
            self._index = self._values.index(self._initial_value)
        else:
            raise PygamingException(f"{self._initial_value} is not a valid initial value as it is not in the values list {self._values}.")

        x_min = self._active_area.left + self.normal_cursor.width//2
        x_max = self._active_area.right - self.normal_cursor.width//2
 
        self._positions = [
              x_max*(t/(len(self._values)-1))
            + x_min*(1 - t/(len(self._values)-1))
            for t in range(len(self._values))
        ]

        self._cursor_position = self._positions[self._index]

    def end(self):
        """Nothing to do at the end of the phase for this widget."""

    def _start_transition(self, new_index):
        """Start a transition."""
        if new_index != self._index:
            # In this case, we start a transition to it.
            self._index = new_index
            self._current_transition = (self._cursor_position, self._positions[self._index])
            self._current_transition_delta = 0

    def update(self, loop_duration: int):
        """Update the slider based on the inputs."""

        # Get a click
        ck1 = self.game.mouse.get_click(1)

        # If the user is clicking:
        if self.is_contact(ck1) and not self.disabled:

            local_x = ck1.make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio).x
            # If the user is clicking on the cursor, we want the cursor to follow the user click
            if self._cursor_position < local_x < self._cursor_position + self._cursor_width:
                self._holding_cursor = True

            # If the user is clicking elsewhere, we want the slider to set a transition to this position.
            elif not self._holding_cursor:

                # We verify that we clicked on a new position
                new_index = self._get_index_of_click(local_x)
                self._start_transition(new_index)

            # In the case we are holding the cursor
            if self._holding_cursor: # We do not use else because we want to execute this after the 1st if.

                local_x = min(max(self._positions[0], local_x), self._positions[-1])
                self._cursor_position = local_x
                self.notify_change()

                self._index = self._get_index_of_click(local_x)

        # In the case the user is not clicking
        else:
            self._holding_cursor = False
            # if we are doing a transition
            if self._current_transition is not None:
                self.notify_change()
                self._current_transition_delta += loop_duration/self._transition_duration
                t = self._transition_func(self._current_transition_delta)
                self._cursor_position = self._current_transition[0]*(1-t) + t*self._current_transition[1]

                # If we finished the transition
                if self._current_transition_delta > 1:
                    self._current_transition_delta = 0
                    self._current_transition = None
                    self._cursor_position = self._positions[self._index]

        # Verify the use of the arrows
        if self.focused and not self.disabled:
            if self.game.keyboard.actions_down['left'] and self._index > 0:
                self._start_transition(max(0, self._index - self._step_wth_arrow))
            if self.game.keyboard.actions_down['right'] and self._index < len(self._values) - 1:
                self._start_transition(min(self._index + self._step_wth_arrow, len(self._values) - 1))


    def _get_index_of_click(self, x):
        """Get the index the closest to the click"""
        return min(range(len(self._positions)), key=lambda i: abs(self._positions[i] - x))

    def _make_normal_surface(self) -> Surface:
        background = self.normal_background
        cursor = self.normal_cursor
        return self._make_surface(background, cursor)

    def _make_focused_surface(self) -> Surface:
        background = self.focused_background
        cursor = self.focused_cursor
        return self._make_surface(background, cursor)

    def _make_disabled_surface(self) -> Surface:
        background = self.disabled_background
        cursor = self.disabled_cursor
        return self._make_surface(background, cursor)

    def _make_surface(self, background: Art, cursor: Art) -> Surface:
        """Make the surface with the cursor and the background."""
        bg = background.get(self.background if self._continue_animation else None, **self.game.settings)
        x = self._cursor_position - self.normal_cursor.width//2
        y = (background.height - cursor.height)//2
        bg.blit(cursor.get(None, **self.game.settings), (x,y))
        return bg
