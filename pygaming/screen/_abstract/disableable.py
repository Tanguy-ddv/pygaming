from .master import Master
from ..art import Art
from .focusable import Focusable, TextualFocusable, GraphicalFocusable
from ..states import WidgetStates
from ...color import Color
from ...database.texts import TextFormatter
from ..anchors import CENTER, Anchor
from .master import Master
from ..art import Art
from ..hitbox import Hitbox
from ..states import WidgetStates

class Disableable(Focusable):

    def __init__(self, master: Master, update_if_invisible: bool, hitbox: Hitbox | None, **kwargs):
        super().__init__(master, update_if_invisible, hitbox, **kwargs)
        self.master.add_child(self, True, True, False, False, False)

    def disable(self):
        """Disable the object."""
        if self.state != WidgetStates.DISABLED:
            self.state = WidgetStates.DISABLED
            self.notify_change()

    def enable(self):
        """Enable the object."""
        if self.state == WidgetStates.DISABLED:
            self.state = WidgetStates.NORMAL
            self.notify_change()

class GraphicalDisableable(GraphicalFocusable, Disableable):

    def __init__(
        self,
        master: Master,
        art: Art,
        focused_art: Art | None = None,
        disabled_art: Art | None = None,
        hitbox: Hitbox = None,
        update_if_invisible: bool = False,
        continue_animation: bool = True,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            hitbox=hitbox,
            art=art,
            focused_art=focused_art,
            update_if_invisible=update_if_invisible,
            continue_animation=continue_animation,
            **kwargs
        )
        self._arts.add(WidgetStates.DISABLED, disabled_art)

    def disable(self):
        """Disable the object."""
        if self.state != WidgetStates.DISABLED:
            self.state = WidgetStates.DISABLED
            self._arts.new_state()
            self.notify_change()

    def enable(self):
        """Enable the object."""
        if self.state == WidgetStates.DISABLED:
            self.state = WidgetStates.NORMAL
            self._arts.new_state()
            self.notify_change()

class TextualDisableable(GraphicalDisableable, TextualFocusable):

    def __init__(
        self,
        master: Master,
        art: Art,
        font: str,
        color: Color,
        text_or_loc: str | TextFormatter,
        hitbox: Hitbox | None = None,
        focused_art: Art | None = None,
        focused_font: str | None = None,
        focused_font_color: Color | None = None,
        disabled_font: str | None = None,
        disabled_font_color: Color | None = None,
        justify: Anchor = CENTER,
        wrap: bool = False,
        update_if_invisible: bool = False,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            art=art,
            focused_art=focused_art,
            focused_font=focused_font,
            focused_font_color=focused_font_color,
            hitbox=hitbox,
            font=font,
            color=color, 
            text_or_loc=text_or_loc,
            justify=justify,
            wrap=wrap,
            update_if_invisible=update_if_invisible,
            **kwargs
        )
        self._fonts.add(WidgetStates.DISABLED, disabled_font, disabled_font_color)
