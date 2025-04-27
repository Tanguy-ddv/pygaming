"""The widget module contains the widget class, which is a base for all widgets."""

from abc import abstractmethod
from ..frame import Frame
from .._abstract import Disableable, TextualDisableable
from ..art import Art
from ..hover import Cursor, Tooltip, Hoverable, TextualHoverable
from ..hitbox import Hitbox
from ...color import Color
from ...database import TextFormatter
from ..anchors import Anchor, CENTER

class Widget(Hoverable, Disableable):

    def __init__(
        self,
        master: Frame,
        art: Art,
        focused_art: Art | None = None,
        disabled_art: Art | None = None,
        hovered_art: Art | None = None,
        hitbox: Hitbox | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = True,
        update_if_invisible: bool = False,
        **kwargs
    ) -> None:
    
        super().__init__(
            master=master,
            art=art,
            disabled_art=disabled_art,
            focused_art=focused_art,
            hitbox=hitbox,
            hovered_art=hovered_art,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            **kwargs
        )

    @abstractmethod
    def get(self):
        """Return the value of the widget input."""
        raise NotImplementedError()

class TextualWidget(TextualHoverable, TextualDisableable):

    def __init__(
        self,
        master: Frame,
        art: Art,
        font: str,
        color: Color,
        text_or_loc: str | TextFormatter,
        focused_art: Art | None = None, 
        focused_font: str | None = None,
        focused_font_color: Color | None = None,
        disabled_art: Art | None = None,
        disabled_font: str | None = None,
        disabled_font_color: Color | None = None,
        hovered_art: Art | None = None,
        hovered_font: str | None = None,
        hovered_font_color: Color | None = None,
        hitbox: Hitbox | None = None,
        tooltip: Tooltip | None = None,
        cursor: Cursor | None = None,
        continue_animation: bool = True,
        update_if_invisible: bool = False,
        justify: Anchor = CENTER,
        **kwargs
    ) -> None:
        
        super().__init__(
            master=master,
            art=art,
            font=font,
            color=color,
            disabled_art=disabled_art,
            focused_art=focused_art,
            hitbox=hitbox,
            text_or_loc=text_or_loc,
            justify=justify,
            hovered_art=hovered_art,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            focused_font=focused_font,
            focused_font_color=focused_font_color,
            disabled_font=disabled_font,
            disabled_font_color=disabled_font_color,
            hovered_font=hovered_font,
            hovered_font_color=hovered_font_color,
            **kwargs
        )

    @abstractmethod
    def get(self):
        """Return the value of the widget input."""
        raise NotImplementedError()
