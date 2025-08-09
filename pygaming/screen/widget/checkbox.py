from typing import Callable, Any, Literal, List

from ...color import Color
from ...database.texts import TextFormatter
from ...screen.anchors import LEFT, AnchorLike, Anchor
from ..art import Art
from ..frame import Frame
from ..hover.cursor import Cursor
from ..hover.tooltip import Tooltip
from ..hitbox import Hitbox
from .widget import CompositeWidget
from .button import MultiStateButton
from .label import Label

class CheckBox(CompositeWidget):

    def __init__(
        self,
        master: Frame,
        label_background: Art,
        label_font: str,
        label_font_color: Color,
        localization_or_text: str | TextFormatter,
        checked_normal_background: Art,
        unchecked_normal_background: Art,
        checked_active_background: Art | None = None,
        checked_focused_background: Art | None = None,
        checked_disabled_background: Art | None = None,
        checked_hovered_background: Art | None = None,
        checked_hitbox: Hitbox | None = None,
        unchecked_active_background: Art | None = None,
        unchecked_focused_background: Art | None = None,
        unchecked_disabled_background: Art | None = None,
        unchecked_hovered_background: Art | None = None,
        unchecked_hitbox: Hitbox | None  = None,
        on_check_command: Callable[[], Any] | None = None,
        on_uncheck_command: Callable[[], Any] | None = None,
        continue_animation: bool = False,
        tooltip: Tooltip = None,
        cursor: Cursor = None,
        label_justify: AnchorLike = LEFT,
        wrap: bool = False,
        update_if_invisible: bool = True,
        box_position: Literal[Anchor.RIGHT, Anchor.LEFT] = Anchor.LEFT,
        **kwargs,
    ):
        size = checked_normal_background.width + label_background.width, max(checked_normal_background.height, label_background.height)
        super().__init__(master, size, update_if_invisible, **kwargs)

        self._box = MultiStateButton(
            self,
            [checked_normal_background, unchecked_normal_background],
            [checked_active_background, unchecked_active_background],
            [checked_focused_background, unchecked_focused_background],
            [checked_disabled_background, unchecked_disabled_background],
            [checked_hovered_background, unchecked_hovered_background],
            [checked_hitbox, unchecked_hitbox],
            tooltip,
            cursor,
            None,
            [on_uncheck_command, on_check_command],
            continue_animation,
            update_if_invisible,
            False
        ).grid(0, int(box_position == Anchor.RIGHT))

        self._label = Label(
            self,
            label_background,
            label_font,
            label_font_color,
            localization_or_text, 
            None,
            None,
            label_justify,
            None, wrap
        ).grid(0, int(box_position == Anchor.LEFT))
    
    def get(self):
        return self._box.get() == 0

    def set(self, value: bool):
        self._box._change(int(not value), True)
        return self

    # def update(self, dt):
    #     print(self, self.state)
    #     print(self._box, self._box.state)
    #     print(self._box.focusable_children[0], self._box.focusable_children[0].state)
    #     print(self._box.focusable_children[1], self._box.focusable_children[1].state)
    #     return super().update(dt)

class RadioButtons(CompositeWidget):

    def __init__(
        self,
        master: Frame,
        label_background: Art,
        label_font: str,
        label_font_color: Color,
        localizations_or_texts: List[str | TextFormatter],
        checked_normal_background: Art,
        unchecked_normal_background: Art,
        checked_active_background: Art | None = None,
        checked_focused_background: Art | None = None,
        checked_disabled_background: Art | None = None,
        checked_hovered_background: Art | None = None,
        checked_hitbox: Hitbox | None = None,
        unchecked_active_background: Art | None = None,
        unchecked_focused_background: Art | None = None,
        unchecked_disabled_background: Art | None = None,
        unchecked_hovered_background: Art | None = None,
        unchecked_hitbox: Hitbox | None  = None,
        on_check_command: Callable[[], Any] | None = None,
        continue_animation: bool = False,
        tooltip: Tooltip = None,
        cursor: Cursor = None,
        label_justify: AnchorLike = LEFT,
        wrap: bool = False,
        update_if_invisible: bool = True,
        box_position: Literal[Anchor.RIGHT, Anchor.LEFT] = Anchor.LEFT,
        **kwargs,
    ):
        size = unchecked_normal_background.width + label_background.width, len(localizations_or_texts)*max(unchecked_normal_background.height, label_background.height)
        super().__init__(master, size, update_if_invisible, **kwargs)

        for i, loc_or_text in enumerate(localizations_or_texts):

            def new_on_check_command(i=i):
                self.set(i)
                if on_check_command is not None:
                    on_check_command()

            def on_uncheck_command(i=i):
                self.set(i)
            
            def refer_or_None(background: Art | None):
                if background is not None: return background.reference()

            _ck = CheckBox(
                self,
                label_background.reference(),
                label_font,
                label_font_color,
                loc_or_text,
                checked_normal_background.reference(),
                unchecked_normal_background.reference(),
                refer_or_None(checked_active_background),
                refer_or_None(checked_focused_background),
                refer_or_None(checked_disabled_background),
                refer_or_None(checked_hovered_background),
                checked_hitbox,
                refer_or_None(unchecked_active_background),
                refer_or_None(unchecked_focused_background),
                refer_or_None(unchecked_disabled_background),
                refer_or_None(unchecked_hovered_background),
                unchecked_hitbox,
                new_on_check_command,
                on_uncheck_command,
                continue_animation,
                tooltip,
                cursor,
                label_justify,
                wrap,
                update_if_invisible,
                box_position
            ).grid(i, 0)

            self.set(0)

    def set(self, index: int):
        for ch in self.focusable_children:
            ch.set(False)
        self.focusable_children[index].set(True)
    
    def get(self):
        """Return the index of the selected item."""
        for i, ch in enumerate(self.focusable_children):
            if ch.get():
                return i
