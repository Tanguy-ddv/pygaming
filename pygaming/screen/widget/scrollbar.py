
from typing import Any, Callable
from pygaming.screen.hitbox import Hitbox
from pygaming.screen.hover.cursor import Cursor
from ..anchors import Anchor
from ..frame import Frame
from .widget import CompositeWidget
from .button import _Button
from .slider import _Slider
from ..art import Art
from ..states import WidgetStates

class HScrollBar(CompositeWidget):

    def __init__(
        self,
        master: Frame,
        target: Frame,
        left_button_normal_background: Art,
        right_button_normal_background: Art,
        slider_normal_background: Art,
        slider_normal_cursor: Art,
        slider_focused_background: Art = None,
        slider_disabled_background: Art = None,
        slider_hovered_background: Art = None,
        slider_focused_cursor: Art = None,
        slider_disabled_cursor: Art = None,
        slider_hovered_cursor: Art = None,
        slider_hitbox: Hitbox | None = None,
        left_button_active_background: Art = None,
        left_button_disabled_background: Art = None, 
        left_button_hovered_background: Art = None,
        left_button_hitbox: Hitbox | None = None,
        right_button_active_background: Art = None,
        right_button_disabled_background: Art = None, 
        right_button_hovered_background: Art = None,
        right_button_hitbox: Hitbox | None = None,
        cursor: Cursor | None = None,
        update_if_invisible: bool = True,
        continue_animation: bool = False,
        left_button_on_click_command: Callable[[],Any] | None = None,
        left_button_on_unclick_command: Callable[[],Any] | None = None,
        right_button_on_click_command: Callable[[],Any] | None = None,
        right_button_on_unclick_command: Callable[[],Any] | None = None,
        step_with_button_or_arrow: int = 1,
        **kwargs
    ):
        size = slider_normal_background.width + left_button_normal_background.width + right_button_normal_background.width, slider_normal_background.height
        super().__init__(master, size, update_if_invisible, **kwargs)
        repeat_delay, repeat_interval = self.game.config.get('repeat_delay', None), self.game.config.get('repeat_interval', None)

        self._slider = _Slider(
            self,
            range(0, target._arts.width - target.camera.width),
            slider_normal_background,
            slider_normal_cursor,
            target.camera.left,
            slider_focused_background,
            slider_focused_cursor,
            slider_disabled_background,
            slider_disabled_cursor,
            slider_hovered_background,
            slider_hovered_cursor,
            slider_hitbox, None, cursor,
            continue_animation, transition_duration=0, update_if_invisible=update_if_invisible,
            direction=Anchor.RIGHT,
            step_with_arrow=step_with_button_or_arrow
        ).place(left_button_normal_background.width, 0)

        self._target = target

        def left_button():
            if left_button_on_click_command is not None:
                left_button_on_click_command()
            if self._slider._index > 0:
                self._slider._start_transition(max(0, self._slider._index - step_with_button_or_arrow))

        def right_button():
            if right_button_on_click_command is not None:
                right_button_on_click_command()

            if self._slider._index < len(self._slider._values) - 1:
                self._slider._start_transition(min(self._slider._index + step_with_button_or_arrow, len(self._slider._values) - 1))

        self._left_button = _Button(
            self,
            left_button_normal_background,
            left_button_active_background,
            None,
            left_button_disabled_background,
            left_button_hovered_background,
            left_button_hitbox, None, cursor, 
            continue_animation, 
            left_button,
            left_button_on_unclick_command,
            update_if_invisible,
            repeat_delay,
            repeat_interval
        ).place(0, 0)

        self._right_button = _Button(
            self,
            right_button_normal_background,
            right_button_active_background,
            None,
            right_button_disabled_background,
            right_button_hovered_background,
            right_button_hitbox, None, cursor, 
            continue_animation, 
            right_button,
            right_button_on_unclick_command,
            update_if_invisible,
            repeat_delay,
            repeat_interval
        ).place(left_button_normal_background.width + slider_normal_background.width, 0)

    def update(self, dt):

        if self.state == WidgetStates.FOCUSED:
            mouse = self.game.mouse.get_wheel()
            if mouse == 1:
                self._right_button._on_click_command()
            elif mouse == -1:
                self._left_button._on_click_command()

        if (cam_x := self._slider.get()) != self._target.camera.left:
            self._target.camera.left = cam_x
            self._target.notify_change()

class VScrollBar(CompositeWidget):

    def __init__(
        self,
        master: Frame,
        target: Frame,
        up_button_normal_background: Art,
        down_button_normal_background: Art,
        slider_normal_background: Art,
        slider_normal_cursor: Art,
        slider_focused_background: Art = None,
        slider_disabled_background: Art = None,
        slider_hovered_background: Art = None,
        slider_focused_cursor: Art = None,
        slider_disabled_cursor: Art = None,
        slider_hovered_cursor: Art = None,
        slider_hitbox: Hitbox | None = None,
        up_button_active_background: Art = None,
        up_button_disabled_background: Art = None, 
        up_button_hovered_background: Art = None,
        up_button_hitbox: Hitbox | None = None,
        down_button_active_background: Art = None,
        down_button_disabled_background: Art = None, 
        down_button_hovered_background: Art = None,
        down_button_hitbox: Hitbox | None = None,
        cursor: Cursor | None = None,
        update_if_invisible: bool = True,
        continue_animation: bool = False,
        up_button_on_click_command: Callable[[],Any] | None = None,
        up_button_on_unclick_command: Callable[[],Any] | None = None,
        down_button_on_click_command: Callable[[],Any] | None = None,
        down_button_on_unclick_command: Callable[[],Any] | None = None,
        step_with_button_or_arrow: int = 1,
        **kwargs
    ):
        size = slider_normal_background.width, slider_normal_background.height + up_button_normal_background.height + down_button_normal_background.height
        super().__init__(master, size, update_if_invisible, **kwargs)
        repeat_delay, repeat_interval = self.game.config.get('repeat_delay', None), self.game.config.get('repeat_interval', None)

        self._slider = _Slider(
            self,
            range(0, target._arts.height - target.camera.height),
            slider_normal_background,
            slider_normal_cursor,
            target.camera.top,
            slider_focused_background,
            slider_focused_cursor,
            slider_disabled_background,
            slider_disabled_cursor,
            slider_hovered_background,
            slider_hovered_cursor,
            slider_hitbox, None, cursor,
            continue_animation, transition_duration=0, update_if_invisible=update_if_invisible,
            direction=Anchor.BOTTOM,
            step_with_arrow=step_with_button_or_arrow
        ).place(0, up_button_normal_background.height)

        self._target = target

        def up_button():
            if up_button_on_click_command is not None:
                up_button_on_click_command()
            if self._slider._index > 0:
                self._slider._start_transition(max(0, self._slider._index - step_with_button_or_arrow))

        def down_button():
            if down_button_on_click_command is not None:
                down_button_on_click_command()

            if self._slider._index < len(self._slider._values) - 1:
                self._slider._start_transition(min(self._slider._index + step_with_button_or_arrow, len(self._slider._values) - 1))

        self._up_button = _Button(
            self,
            up_button_normal_background,
            up_button_active_background,
            None,
            up_button_disabled_background,
            up_button_hovered_background,
            up_button_hitbox, None, cursor, 
            continue_animation, 
            up_button,
            up_button_on_unclick_command,
            update_if_invisible,
            repeat_delay,
            repeat_interval
        ).place(0, 0)

        self._down_button = _Button(
            self,
            down_button_normal_background,
            down_button_active_background,
            None,
            down_button_disabled_background,
            down_button_hovered_background,
            down_button_hitbox, None, cursor, 
            continue_animation, 
            down_button,
            down_button_on_unclick_command,
            update_if_invisible,
            repeat_delay,
            repeat_interval
        ).place(0, up_button_normal_background.height + slider_normal_background.height)

    def update(self, dt):

        if self.state == WidgetStates.FOCUSED:
            mouse = self.game.mouse.get_wheel()
            if mouse == 1:
                self._up_button._on_click_command()
            elif mouse == -1:
                self._down_button._on_click_command()

        if (cam_y := self._slider.get()) != self._target.camera.top:
            self._target.camera.top = cam_y
            self._target.notify_change()
