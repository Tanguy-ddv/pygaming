"""The Slider is Widget used to enter a numeric value within an interval."""
from typing import Optional, Sequence, Any, Literal, Callable
from pygame import Surface
from ZOCallable import ZOCallable, verify_ZOCallable
from ZOCallable.functions import linear
from .._abstract import Arts
from ..states import WidgetStates
from .widget import Widget, TextualWidget
from ..frame import Frame
from ..art import Art
from ..hover import Cursor, Tooltip
from ..hitbox import Hitbox
from ..anchors import Anchor
from ...color import Color
from ...error import PygamingException

class _Slider(Widget):
    """Base Slider class."""

    def __init__(
        self,
        master: Frame,
        values: Sequence,
        art: Art,
        normal_cursor: Art,
        initial_value: Optional[Any] = None,
        focused_art: Optional[Art] = None,
        focused_cursor: Optional[Art] = None,
        disabled_art: Optional[Art] = None,
        disabled_cursor: Optional[Art] = None,
        hovered_art: Optional[Art] = None,
        hovered_cursor: Optional[Art] = None,
        hitbox: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        transition_function: ZOCallable = linear,
        transition_duration: int = 300, # [ms]
        update_if_invisible: bool = True,
        step_wth_arrow: int = 1,
        direction: Literal[Anchor.TOP, Anchor.RIGHT, Anchor.LEFT, Anchor.BOTTOM] = Anchor.RIGHT,
        command: Optional[Callable[[], Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            art=art,
            focused_art=focused_art,
            disabled_art=disabled_art,
            hovered_art=hovered_art,
            hitbox=hitbox,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            **kwargs
        )

        self._cursor_arts = Arts(normal_cursor)
        self._cursor_arts.set_continue_animation(continue_animation)
        self._cursor_arts.add(WidgetStates.DISABLED, disabled_cursor)
        self._cursor_arts.add(WidgetStates.FOCUSED, focused_cursor)
        self._cursor_arts.add(WidgetStates.HOVERED, hovered_cursor)

        # initial value and index
        self._values= list(values)
        self._initial_value = initial_value
        self._index = 0
        self._positions = []

        self._cursor_width = self._cursor_arts.width
        self._cursor_height = self._cursor_arts.height
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

    def begin(self, **kwargs):
        # the positions of the cursor for each value
        super().begin(**kwargs)
        if self._initial_value is None:
            self._index = 0
        elif self._initial_value in self._values:
            self._index = self._values.index(self._initial_value)
        else:
            raise ValueError(f"{self._initial_value} is not a valid initial value as it is not in the values list {self._values}.")

        if self._direction in [Anchor.RIGHT, Anchor.LEFT]:

            pos_min = self.hitbox.left + self._cursor_width//2
            pos_max = self.hitbox.right - self._cursor_width//2
        
        else:

            pos_min = self.hitbox.top + self._cursor_height//2
            pos_max = self.hitbox.bottom - self._cursor_height//2
 
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

    def update(self, dt: int):
        """Update the slider based on the inputs."""

        # Update the cursor image
        if (self.on_master and self.is_visible()) or self._update_if_invisible:
            has_changed = self._cursor_arts.update(dt, self.state)
            if has_changed:
                self.notify_change()

        # Get a click
        ck1 = self.game.mouse.get_click(1)

        # If the user is clicking:
        if self.is_contact(ck1) and not self.state == WidgetStates.DISABLED:
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
                    self._current_transition_delta += dt/self._transition_duration
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
        if self.state == WidgetStates.FOCUSED:
            match self._direction:
                case Anchor.RIGHT:
                    increase = 'right'
                    decrease = 'left'
                case Anchor.LEFT:
                    increase = 'left'
                    decrease = 'right'
                case Anchor.BOTTOM:
                    increase = 'down'
                    decrease = 'up'
                case Anchor.TOP:
                    increase = 'up'
                    decrease = 'down'
                case _:
                    raise PygamingException(f"""
                        This slider do not have a direction set, should be one of
                        Anchor.LEFT, Anchor.RIGHT, Anchor.TOP, Anchor.BOTTOM
                        but got {self._direction}.
                        """)
            
            if self.game.keyboard.actions_down[decrease] and self._index > 0:
                self._start_transition(max(0, self._index - self._step_wth_arrow))
                if self._command is not None:
                    self._command()
            
            if self.game.keyboard.actions_down[increase] and self._index < len(self._values) - 1:
                self._start_transition(min(self._index + self._step_wth_arrow, len(self._values) - 1))
                if self._command is not None:
                    self._command()

    def _get_index_of_click(self, x):
        """Get the index the closest to the click"""
        return min(range(len(self._positions)), key=lambda i: abs(self._positions[i] - x))

    def make_surface(self) -> Surface:
        """Make the surface with the cursor and the background."""

        bg = self._arts.get(self.state, **self.game.settings)
        cursor = self._cursor_arts.get(self.state, **self.game.settings)
        if self._direction in [Anchor.LEFT, Anchor.RIGHT]:
            x = self._cursor_position - self._cursor_width//2
            y = (bg.get_height() - self._cursor_height)//2
        else:
            y = self._cursor_position - self._cursor_height//2
            x = (bg.get_width() - self._cursor_width)//2
        bg.blit(cursor, (x,y))
        return bg

class Slider(_Slider):
    """The Slider is a widget that is used to select a value in a given range."""

    def __init__(
        self,
        master: Frame,
        values: Sequence,
        normal_background: Art,
        normal_cursor: Art,
        initial_value: Any | None = None,
        focused_background: Art | None = None,
        focused_cursor: Art | None = None,
        disabled_background: Art | None = None,
        disabled_cursor: Art | None = None,
        hovered_background: Art | None = None,
        hovered_cursor: Art | None = None,
        hitbox: Hitbox | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        transition_function: ZOCallable = linear,
        transition_duration: int = 300,
        update_if_invisible: bool = True,
        step_wth_arrow: int = 1,
        direction: Literal[Anchor.TOP, Anchor.RIGHT, Anchor.LEFT, Anchor.BOTTOM] = Anchor.RIGHT,
        command: Callable[[], Any] | None = None,
        **kwargs
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
            hitbox,
            tooltip,
            cursor,
            continue_animation,
            transition_function,
            transition_duration,
            update_if_invisible,
            step_wth_arrow,
            direction,
            command,
            **kwargs
        )

class TextSlider(_Slider, TextualWidget):
    """A Slider that can display texts."""

    def __init__(
        self,
        master: Frame,
        values: Sequence,
        normal_background: Art,
        normal_cursor: Art,
        normal_font: str,
        normal_font_color: Color,
        initial_value: Optional[Any] = None,
        focused_background: Optional[Art] = None,
        focused_cursor: Optional[Art] = None,
        focused_font: str | None = None,
        focused_font_color: Color | None = None,
        disabled_background: Optional[Art] = None,
        disabled_cursor: Optional[Art] = None,
        disabled_font: str | None = None,
        disabled_font_color: Color | None = None,
        hovered_background: Optional[Art] = None,
        hovered_cursor: Optional[Art] = None,
        hovered_font: str | None = None,
        hovered_font_color: Color | None = None,
        hitbox: Optional[Hitbox] = None,
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
        - hitbox: Rect. The Rectangle in the bacground that represent the active part of the slider. if None, then it is the whole background.
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
            master=master,
            values=values,
            art=normal_background,
            normal_cursor=normal_cursor,
            initial_value=initial_value,
            focused_art=focused_background,
            focused_cursor=focused_cursor,
            disabled_art=disabled_background,
            disabled_cursor=disabled_cursor,
            hovered_art=hovered_background,
            hovered_cursor=hovered_cursor,
            hitbox=hitbox,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            transition_function=transition_function,
            transition_duration=transition_duration,
            update_if_invisible=update_if_invisible,
            step_wth_arrow=step_wth_arrow,
            direction=direction,
            command=command,
            font=normal_font,
            color=normal_font_color,
            text_or_loc="",
            focused_font=focused_font,
            focused_font_color=focused_font_color,
            disabled_font=disabled_font,
            disabled_font_color=disabled_font_color,
            hovered_font=hovered_font,
            hovered_font_color=hovered_font_color,
            justify=justify
        )

        self._text_factory = text_factory

    def make_surface(self):
        """Return the surface of the Label."""
        bg = Slider.make_surface(self)
        rendered_text = self._fonts.render(self.game.typewriter, self.state, self._text_factory(self.get()), None, self._justify)
        text_width, text_height = rendered_text.get_size()
        just_x = self._justify[0]*(self._arts.width - text_width)
        just_y = self._justify[1]*(self._arts.height - text_height)
        bg.blit(rendered_text, (just_x, just_y))
        return bg
