"""the hoverable module contains the hoverable class, an abstract for visuals having a tooltip or a cursor."""
from ...screen.art import Art
from .._abstract import Collideable, GraphicalChild, Master, Textual
from ..states import WidgetStates
from .cursor import Cursor
from .tooltip import Tooltip
from ..hitbox import Hitbox
from ...color import Color
from ..anchors import Anchor, CENTER
from ...database import TextFormatter

class Hoverable(GraphicalChild, Collideable):
    """An Hoverable is a placable that can display a tooltip or a cursor when hovered."""

    def __init__(
        self,
        master: Master,
        art: Art,
        hitbox: Hitbox | None = None,
        hovered_art: Art | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = True,
        update_if_invisible: bool = False,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            art=art,
            hitbox=hitbox,
            update_if_invisible=update_if_invisible,
            **kwargs
        )
        self._arts.set_continue_animation(continue_animation)
        self._arts.add(WidgetStates.HOVERED, hovered_art)
        self.master.add_child(self, False, False, True, True, False, True)
        self.tooltip = tooltip
        self.cursor = cursor
        self._previous_state = WidgetStates.NORMAL
    
    def begin(self):
        super().begin()
        if self.tooltip is not None:
            self.tooltip.begin(self.master.game.settings)

    def finish(self):
        super().finish()
        if self.tooltip is not None:
            self.tooltip.finish()

    def get_hover(self, pos):
        """Return the tooltip and cursor of the hoverable."""
        if self.is_contact(pos):
            self.set_hover()
            return self.tooltip, self.cursor
        else:
            self.unset_hover()
            return None, None

    def unset_hover(self):
        if self.state == WidgetStates.HOVERED:
            self.state = self._previous_state
            self._arts.new_state()
            self.notify_change()

    def set_hover(self):
        if self.state == WidgetStates.NORMAL:
            self._previous_state = self.state
            self.state = WidgetStates.HOVERED
            self._arts.new_state()
            self.notify_change()

class TextualHoverable(Hoverable, Textual):

    def __init__(
        self,
        master: Master,
        art: Art,
        font: str,
        text_or_loc: str | TextFormatter,
        color: Color,
        hitbox: Hitbox | None = None,
        hovered_art: Art | None = None,
        hovered_font: str | None = None,
        hovered_color: Color | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = True,
        justify: Anchor = CENTER,
        wrap: bool = False,
        update_if_invisible: bool = False,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            art=art,
            hitbox=hitbox,
            hovered_art=hovered_art,
            tooltip=tooltip,
            cursor=cursor,
            font=font,
            color=color,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            text_or_loc=text_or_loc,
            justify=justify,
            wrap=wrap,
            **kwargs
        )
        self._fonts.add(WidgetStates.HOVERED, hovered_font, hovered_color)
