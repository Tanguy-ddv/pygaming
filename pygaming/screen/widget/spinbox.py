from typing import Any, Callable, Optional, Sequence, Literal

from string import ascii_letters, punctuation
from ..frame import Frame
from .widget import CompositeWidget
from .entry import Entry, _DEFAULT_CARET_FREQUENCY, _DEFAULT_CARET_WIDTH, _DEFAULT_MAX_LENGTH
from .button import _Button
from ..art import Art
from ..hitbox import Hitbox
from ..hover import Cursor, Tooltip
from ...color import Color
from ..anchors import LEFT, AnchorLike

class SpinBox(CompositeWidget):

    def __init__(
        self,
        master: Frame,
        up_button_normal_background: Art,
        down_button_normal_background: Art,
        entry_normal_background: Art,
        entry_normal_font: str,
        entry_normal_font_color: Color,
        values: Sequence[int | float],
        initial_value: int | float | None = None,
        entry_focused_background: Optional[Art] = None,
        entry_focused_font: Optional[str] = None,
        entry_focused_font_color: Optional[Color] = None,
        entry_disabled_background: Optional[Art] = None,
        entry_disabled_font: Optional[str] = None,
        entry_disabled_font_color: Optional[Color] = None,
        entry_hovered_background: Optional[str] = None,
        entry_hovered_font: Optional[str] = None,
        entry_hovered_font_color: Optional[Color] = None,
        entry_invalid_background: Optional[str] = None,
        entry_invalid_font: Optional[str] = None,
        entry_invalid_font_color: Optional[Color] = None,
        entry_hitbox: Optional[Hitbox] = None,
        entry_caret_frequency: int = _DEFAULT_CARET_FREQUENCY,
        entry_caret_width: int = _DEFAULT_CARET_WIDTH,
        entry_max_length: int = _DEFAULT_MAX_LENGTH,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        up_button_active_background: Art = None,
        up_button_disabled_background: Art = None, 
        up_button_hovered_background: Art = None,
        up_button_hitbox: Hitbox | None = None,
        down_button_active_background: Art = None,
        down_button_disabled_background: Art = None, 
        down_button_hovered_background: Art = None,
        down_button_hitbox: Hitbox | None = None,
        justify: AnchorLike = LEFT,
        accept_float: bool = True,
        update_if_invisible: bool = True,
        up_button_on_click_command: Callable[[], Any] | None = None,
        up_button_on_unclick_command: Callable[[], Any] | None = None,
        down_button_on_click_command: Callable[[], Any] | None = None,
        down_button_on_unclick_command: Callable[[], Any] | None = None,
        vertical_arrows: bool = True, # Tkinter like, other option is left and right
        ciclable: bool = False
    ):
        if vertical_arrows:
            size = (entry_normal_background.width + up_button_normal_background.width, max(entry_normal_background.height, up_button_normal_background.height + down_button_normal_background.height))
        else:
            size = (entry_normal_background.width + up_button_normal_background.width + down_button_normal_background.width,  max(entry_normal_background.height, up_button_normal_background.height, down_button_normal_background.height))
        super().__init__(master, size, update_if_invisible)
        self._values = list(values)
        if initial_value is None:
            initial_value = values[0]
        self._initial_value = initial_value
        

        def vfunc(input):
            if accept_float:
                return float(input) in self._values
            else:
                return int(input) in self._values

        self._entry = Entry(
            self,
            entry_normal_background,
            entry_normal_font,
            entry_normal_font_color,
            entry_focused_background,
            entry_focused_font,
            entry_focused_font_color,
            entry_disabled_background,
            entry_disabled_font,
            entry_disabled_font_color,
            entry_hovered_background,
            entry_hovered_font,
            entry_hovered_font_color,
            initial_value,
            '',
            (ascii_letters + punctuation).replace('.', '') if accept_float else ascii_letters + punctuation,
            entry_hitbox,
            tooltip,
            cursor,
            continue_animation,
            justify,
            entry_caret_frequency,
            entry_caret_width,
            entry_max_length,
            update_if_invisible,
            '',
            None,
            None,
            entry_invalid_background,
            entry_invalid_font,
            entry_invalid_font_color,
            vfunc,
            None,
            False
        )
        if vertical_arrows:
            self._entry.grid(0, 0, None, rowspan=2)
        else:
            self._entry.grid(0, 1)


        def up_func():
            if up_button_on_click_command is not None:
                up_button_on_click_command
            v = self._entry.get()
            if accept_float:
                v = float(v)
            else:
                v = int(v)
            if v in self._values:
                idx = self._values.index(v)
                if idx < len(self._values)-1:
                    self._entry.text = str(self._values[idx+1])
                elif ciclable:
                    self._entry.text = str(self._values[(idx+1)%len(self._values)])
            else:
                 self._entry.text = str(self._values[0])
                
            self._entry.notify_change()

        repeat_delay, repeat_interval = self.game.config.get('repeat_delay', None), self.game.config.get('repeat_interval', None)

        self._button_up = _Button(
            self,
            up_button_normal_background,
            up_button_active_background,
            None,
            up_button_disabled_background,
            up_button_hovered_background,
            up_button_hitbox,
            None,
            cursor,
            continue_animation,
            up_func,
            up_button_on_unclick_command,
            False,
            repeat_delay,
            repeat_interval,
        )

        if vertical_arrows:
            self._button_up.grid(0, 1)
        else:
            self._button_up.grid(0, 2)
    
        def down_func():
            if down_button_on_click_command is not None:
                down_button_on_click_command()
            v = self._entry.get()
            if accept_float:
                v = float(v)
            else:
                v = int(v)
            if v in self._values:
                idx = self._values.index(v)
                if idx > 0:
                    self._entry.text = str(self._values[idx-1])
                elif ciclable:
                    self._entry.text = str(self._values[(idx-1)%len(self._values)])
            else:
                 self._entry.text = str(self._values[-1])
            self._entry.notify_change()

        self._button_down = _Button(
            self,
            down_button_normal_background,
            down_button_active_background,
            None,
            down_button_disabled_background,
            down_button_hovered_background,
            down_button_hitbox,
            None,
            cursor,
            continue_animation,
            down_func,
            down_button_on_unclick_command,
            False,
            repeat_delay,
            repeat_interval,
        )

        if vertical_arrows:
            self._button_up.grid(1, 1)
        else:
            self._button_up.grid(0, 0)
        