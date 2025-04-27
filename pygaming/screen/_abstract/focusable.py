from ...color import Color
from ...database.texts import TextFormatter
from ..anchors import CENTER, Anchor
from .master import Master
from ..art import Art
from .collideable import Collideable
from .graphical import GraphicalChild
from .textual import Textual
from ..hitbox import Hitbox
from ..states import WidgetStates


class Focusable(GraphicalChild, Collideable):

    def __init__(
        self,
        master: Master,
        art: Art,
        focused_art: Art,
        hitbox: Hitbox | None = None,
        update_if_invisible: bool = False,
        continue_animation: bool = True,
        **kwargs
    ) -> None:
        super().__init__(master=master, art=art, hitbox=hitbox, update_if_invisible=update_if_invisible, **kwargs)
        self._arts.set_continue_animation(continue_animation)
        self._arts.add(WidgetStates.FOCUSED, focused_art)
        self.master.add_child(self, True, False, False, False, False, False)

    def focus(self):
        """Focus the object."""
        if self.state in [WidgetStates.NORMAL, WidgetStates.HOVERED]:
            self.state = WidgetStates.FOCUSED
            self._arts.new_state()
            self.notify_change()

    def unfocus(self):
        """Unfocus the object."""
        if self.state == WidgetStates.FOCUSED:
            self.state = WidgetStates.NORMAL
            self._arts.new_state()
            self.notify_change()

class TextualFocusable(Focusable, Textual):

    def __init__(
        self,
        master: Master,
        art: Art,
        font: str,
        color: Color,
        text_or_loc: str | TextFormatter,
        focused_art: Art | None = None,
        focused_font: str | None = None,
        focused_font_color: Color | None = None,
        justify: Anchor = CENTER,
        hitbox: Hitbox | None = None,
        wrap: bool = False,
        update_if_invisible: bool = False,
        continue_animation: bool = True,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            art=art,
            focused_art=focused_art,
            hitbox=hitbox,
            font=font,
            color=color, 
            text_or_loc=text_or_loc,
            justify=justify,
            wrap=wrap,
            update_if_invisible=update_if_invisible,
            continue_animation=continue_animation,
            **kwargs
        )
        self._fonts.add(WidgetStates.FOCUSED, focused_font, focused_font_color)
