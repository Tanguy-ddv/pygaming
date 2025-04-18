"""The Slider is Widget used to enter a numeric value within an interval."""
from typing import Optional, Sequence, Any, Literal, Callable
from pygame import Surface
from ZOCallable import ZOCallable, verify_ZOCallable
from ZOCallable.functions import linear
from .widget import Widget
from ..frame import Frame
from ..art import Art
from ..cursor import Cursor
from ..tooltip import Tooltip
from ..hitbox import Hitbox
from ..anchors import Anchor

class Slider(Widget):
    """The Slider is a widget that is used to select a value in a given range."""

    def __init__(
        self,
        master: Frame,
        values: Sequence,
        normal_background: Art,
        normal_cursor: Art,
        initial_value: Optional[Any] = None,
        focused_background: Optional[Art] = None,
        focused_cursor: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        disabled_cursor: Optional[Art] = None,
        hovered_background: Optional[Art] = None,
        hovered_cursor: Optional[Art] = None,
        active_area: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        transition_function: ZOCallable = linear,
        transition_duration: int = 300, # [ms]
        update_if_invisible: bool = True,
        step_wth_arrow: int = 1,
        direction: Literal[Anchor.TOP, Anchor.RIGHT, Anchor.LEFT, Anchor.BOTTOM] = Anchor.RIGHT,
        command: Optional[Callable[[], Any]] = None,
    ) -> None:
        """
        A Slider is a widget that is used to select a value in a given range by moving a cursor from left to right on a background.

        Params:
        ---
        - master: Frame. The Frame in which this widget is placed.
        - values: Iterable, the ordered list of values from which the slider can select.
        - normal_background: Art: The art used as the background of the slider when it is neither focused nor disabled.
        - normal_cursor: Art : The art used as the cursor of the slider when it is neither focused nor disabled.
        - initial_value: Any, The initial value set to the cursor. If None, use the first value.
        - focused_background: Art : The art used as the background of the slider when it is focused.
        - focused_cursor: Art : The art used as the cursor of the slider when it is focused.
        - disabled_background: Art : The art used as the background of the slider when it is disabled.
        - disabled_cursor: Art : The art used as the cursor of the slider when it is disabled.
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the slider. if None, then it is the whole background.
        - tooltip: Tooltip, the tooltip to show when the slider is hovered.
        - cursor: Cursor The cursor of the mouse to use when the widget is hovered
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - transition_function: func [0, 1] -> [0, 1] A function that represent the position of the cursor during a transition given the transition duration.
            Default is lambda x:x. For an accelerating transition, use lambda x:x**2, for a decelerating transition, lambda x:x**(1/2), or other.
            Conditions: transition_function(0) = 0, transition_function(1) = 1
        - transition_duration: int [ms], the duration of the transition in ms.
        - update_if_invisible: bool, set to True if you want the widget to be update even if it is not visible. Default is True to finish the transitions.
        - step_wth_arrow: int, the number of step the slider should do when it is updated with an arrow of the keyboard. Default is 1
        - direction: the direction of the slider when its internal index increases. If BOTTOM or TOP are selected, then the slider is vertical
        otherwise, it is horizontal. If LEFT is selected, the last value of the values Sequence is selected when the cursor is at its left-most position
        and so on. default is RIGHT.
        """
        super().__init__(
            master,
            normal_background,
            focused_background,
            disabled_background,
            hovered_background,
            active_area,
            tooltip,
            cursor,
            continue_animation,
            update_if_invisible
        )

        self.normal_cursor = normal_cursor
        self.focused_cursor = focused_cursor if focused_cursor else normal_cursor
        self.disabled_cursor = disabled_cursor if disabled_cursor else normal_cursor
        self.hovered_cursor = hovered_cursor if hovered_cursor else normal_cursor

        # initial value and index
        self._values= list(values)
        self._initial_value = initial_value
        self._index = 0
        self._positions = []

        self._cursor_width = self.normal_cursor.width
        self._cursor_height = self.normal_cursor.height
        self._holding_cursor = False

        # Transition-related attributes
        verify_ZOCallable(transition_function)
        self._transition_func = transition_function
        self._transition_duration = transition_duration
        self._current_transition = None
        self._current_transition_delta = 0
        self._cursor_position = None

        self._step_wth_arrow = step_wth_arrow

        self._direction = direction
        self._command = command

    def get(self):
        """Return the value selected by the player."""
        return self._values[self._index]

    def start(self):
        # the positions of the cursor for each value
        super().start()
        if self._initial_value is None:
            self._index = 0
        elif self._initial_value in self._values:
            self._index = self._values.index(self._initial_value)
        else:
            raise ValueError(f"{self._initial_value} is not a valid initial value as it is not in the values list {self._values}.")

        if self._direction in [Anchor.RIGHT, Anchor.LEFT]:

            pos_min = self._active_area.left + self._cursor_width//2
            pos_max = self._active_area.right - self._cursor_width//2
        
        else:

            pos_min = self._active_area.top + self._cursor_height//2
            pos_max = self._active_area.bottom - self._cursor_height//2
 
        self._positions = [
              pos_max*(t/(len(self._values)-1))
            + pos_min*(1 - t/(len(self._values)-1))
            for t in range(len(self._values))
        ]

        if self._direction in [Anchor.LEFT, Anchor.TOP]:
            self._positions.reverse()
            self._index = len(self._positions) - self._index - 1

        self._cursor_position = self._positions[self._index]

    def _start_transition(self, new_index):
        """Start a transition."""
        if new_index != self._index:
            # In this case, we start a transition to it.
            self._index = new_index
            self._current_transition = (self._cursor_position, self._positions[self._index])
            self._current_transition_delta = 0

    def update(self, loop_duration: int):
        """Update the slider based on the inputs."""

        # Update the cursor image
        if (self.on_master and self.is_visible()) or self._update_if_invisible:
            if not self._continue_animation:
                if self.disabled:
                    has_changed = self.disabled_cursor.update(loop_duration)
                elif self.focused:
                    has_changed = self.focused_cursor.update(loop_duration)
                elif self._hovered:
                    has_changed = self.hovered_cursor.update(loop_duration)
                else:
                    has_changed = self.normal_cursor.update(loop_duration)
                if has_changed:
                    self.notify_change()
            else:
                has_changed = self.normal_cursor.update(loop_duration)
                if has_changed:
                    self.notify_change()

        # Get a click
        ck1 = self.game.mouse.get_click(1)

        # If the user is clicking:
        if self.is_contact(ck1) and not self.disabled:
            if self._command is not None:
                self._command()

            if self._direction in [Anchor.LEFT, Anchor.RIGHT]:

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
                    
                    if self._direction == Anchor.LEFT:
                        local_x = max(min(self._positions[0], local_x), self._positions[-1])
                    else:
                        local_x = min(max(self._positions[0], local_x), self._positions[-1])
                    self._index = self._get_index_of_click(local_x)
                    
                    self._cursor_position = local_x
                    self.notify_change()
            else:
                local_y = ck1.make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio).y
                # If the user is clicking on the cursor, we want the cursor to follow the user click
                if self._cursor_position < local_y < self._cursor_position + self._cursor_height:
                    self._holding_cursor = True

                # If the user is clicking elsewhere, we want the slider to set a transition to this position.
                elif not self._holding_cursor:

                    # We verify that we clicked on a new position
                    new_index = self._get_index_of_click(local_y)
                    self._start_transition(new_index)

                # In the case we are holding the cursor
                if self._holding_cursor: # We do not use else because we want to execute this after the 1st if.
                    
                    if self._direction == Anchor.TOP:
                        local_y = max(min(self._positions[0], local_y), self._positions[-1])
                    else:
                        local_y = min(max(self._positions[0], local_y), self._positions[-1])
                    self._index = self._get_index_of_click(local_y)
                    
                    self._cursor_position = local_y
                    self.notify_change()

        # In the case the user is not clicking
        else:
            self._holding_cursor = False
            # if we are doing a transition
            if self._current_transition is not None:
                self.notify_change()
                if self._transition_duration > 0:
                    self._current_transition_delta += loop_duration/self._transition_duration
                else:
                    self._current_transition_delta = 1.01 # The transition is instantaneous
                t = self._transition_func(self._current_transition_delta)
                self._cursor_position = self._current_transition[0]*(1-t) + t*self._current_transition[1]

                # If we finished the transition
                if self._current_transition_delta >= 1:
                    self._current_transition_delta = 0
                    self._current_transition = None
                    self._cursor_position = self._positions[self._index]

        # Verify the use of the arrows
        if self._direction in [Anchor.LEFT, Anchor.RIGHT] and self.focused and not self.disabled:
            if self.anchor == Anchor.RIGHT:
                right = 'right'
                left = 'left'
            else:
                right = 'left'
                left = 'right'
            if self.game.keyboard.actions_down[left] and self._index > 0:
                self._start_transition(max(0, self._index - self._step_wth_arrow))
                if self._command is not None:
                    self._command()
            if self.game.keyboard.actions_down[right] and self._index < len(self._values) - 1:
                self._start_transition(min(self._index + self._step_wth_arrow, len(self._values) - 1))
                if self._command is not None:
                    self._command()
        elif self.focused and not self.disabled:
            if self.anchor == Anchor.RIGHT:
                up = 'up'
                down = 'down'
            else:
                up = 'down'
                down = 'up'
            if self.game.keyboard.actions_down[up] and self._index > 0:
                self._start_transition(max(0, self._index - self._step_wth_arrow))
                if self._command is not None:
                    self._command()
            if self.game.keyboard.actions_down[down] and self._index < len(self._values) - 1:
                self._start_transition(min(self._index + self._step_wth_arrow, len(self._values) - 1))
                if self._command is not None:
                    self._command()

    def _get_index_of_click(self, x):
        """Get the index the closest to the click"""
        return min(range(len(self._positions)), key=lambda i: abs(self._positions[i] - x))

    def _make_normal_surface(self) -> Surface:
        return self._make_surface(self.normal_background, self.normal_cursor)

    def _make_focused_surface(self) -> Surface:
        return self._make_surface(self.focused_background, self.focused_cursor)

    def _make_disabled_surface(self) -> Surface:
        return self._make_surface(self.disabled_background, self.disabled_cursor)

    def _make_hovered_surface(self) -> Surface:
        return self._make_surface(self.hovered_background, self.hovered_cursor)

    def _make_surface(self, background: Art, cursor: Art) -> Surface:
        """Make the surface with the cursor and the background."""
        bg = background.get(self.background if self._continue_animation else None, **self.game.settings)
        if self._direction in [Anchor.LEFT, Anchor.RIGHT]:
            x = self._cursor_position - self.normal_cursor.width//2
            y = (background.height - cursor.height)//2
        else:
            y = self._cursor_position - self.normal_cursor.height//2
            x = (background.width - cursor.width)//2
        bg.blit(cursor.get(self.normal_cursor if self._continue_animation else None, **self.game.settings), (x,y))
        return bg

class TextSlider(Slider):
    """A Slider that can display texts."""

    def __init__(
        self,
        master: Frame,
        values: Sequence,
        normal_background: Art,
        normal_cursor: Art,
        font: str,
        font_color: str,
        initial_value: Optional[Any] = None,
        focused_background: Optional[Art] = None,
        focused_cursor: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        disabled_cursor: Optional[Art] = None,
        hovered_background: Optional[Art] = None,
        hovered_cursor: Optional[Art] = None,
        active_area: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        transition_function: ZOCallable = linear,
        transition_duration: int = 300, # [ms]
        update_if_invisible: bool = True,
        text_factory: Callable[[Any], str] = str,
        justify: Anchor = Anchor.CENTER_CENTER,
        step_wth_arrow: int = 1,
        direction: Literal[Anchor.TOP, Anchor.RIGHT, Anchor.LEFT, Anchor.BOTTOM] = Anchor.RIGHT,
        command: Optional[Callable[[], Any]] = None,
    ) -> None:
        """
        A Slider is a widget that is used to select a value in a given range by moving a cursor from left to right on a background.

        Params:
        ---
        - master: Frame. The Frame in which this widget is placed.
        - values: Iterable, the ordered list of values from which the slider can select.
        - normal_background: Art: The art used as the background of the slider when it is neither focused nor disabled.
        - normal_cursor: Art : The art used as the cursor of the slider when it is neither focused nor disabled.
        - initial_value: Any, The initial value set to the cursor. If None, use the first value.
        - focused_background: Art : The art used as the background of the slider when it is focused.
        - focused_cursor: Art : The art used as the cursor of the slider when it is focused.
        - disabled_background: Art : The art used as the background of the slider when it is disabled.
        - disabled_cursor: Art : The art used as the cursor of the slider when it is disabled.
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the slider. if None, then it is the whole background.
        - tooltip: Tooltip, the tooltip to show when the slider is hovered.
        - cursor: Cursor The cursor of the mouse to use when the widget is hovered
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - transition_function: func [0, 1] -> [0, 1] A function that represent the position of the cursor during a transition given the transition duration.
            Default is lambda x:x. For an accelerating transition, use lambda x:x**2, for a decelerating transition, lambda x:x**(1/2), or other.
            Conditions: transition_function(0) = 0, transition_function(1) = 1
        - transition_duration: int [ms], the duration of the transition in ms.
        - update_if_invisible: bool, set to True if you want the widget to be update even if it is not visible. Default is True to finish the transitions.
        - step_wth_arrow: int, the number of step the slider should do when it is updated with an arrow of the keyboard. Default is 1
        - direction: the direction of the slider when its internal index increases. If BOTTOM or TOP are selected, then the slider is vertical
        otherwise, it is horizontal. If LEFT is selected, the last value of the values Sequence is selected when the cursor is at its left-most position
        and so on. default is RIGHT.
        """
        super().__init__(
            master,
            values,
            normal_background,
            normal_cursor,
            initial_value,
            focused_background,
            focused_cursor,
            disabled_background,
            disabled_cursor,
            hovered_background,
            hovered_cursor,
            active_area,
            tooltip,
            cursor,
            continue_animation,
            transition_function,
            transition_duration,
            update_if_invisible,
            step_wth_arrow,
            direction,
            command
        )
        self._font = font
        self._font_color = font_color
        self._text_factory = text_factory
        self._justify = justify

    def _make_surface(self, background, cursor):
        """Return the surface of the Label."""
        bg = Slider._make_surface(self, background, cursor)
        rendered_text = self.game.typewriter.render(self._font, self._text_factory(self.get()), self._font_color, None, self._justify)
        text_width, text_height = rendered_text.get_size()
        just_x = self._justify[0]*(self.background.width - text_width)
        just_y = self._justify[1]*(self.background.height - text_height)
        bg.blit(rendered_text, (just_x, just_y))
        return bg