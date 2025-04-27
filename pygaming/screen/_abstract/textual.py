from functools import cache
from pygame import Surface
from ..art import Art
from ...color import Color
from ..states import WidgetStates, States
from ...database import TextFormatter, TypeWriter
from .graphical import Graphical
from ..anchors import LEFT, Anchor, CENTER
from ...settings import Settings

class Fonts:

    def __init__(self, font: str, color: Color) -> None:
        """
        each font object is a string and a color
        """
        self._fonts: dict[States, str] = {WidgetStates.NORMAL : font}
        self._colors: dict[States, str] = {WidgetStates.NORMAL : color}
    
    def add(self, state: States, font: str | None, color: Color | None):
        self._fonts[state] = font
        self._colors[state] = color
    
    def get(self, state: States = WidgetStates.NORMAL) -> tuple[str, Color]:
        font = self._fonts.get(state, None)
        if font is None:
            font = self._fonts.get(WidgetStates.NORMAL)

        color = self._colors.get(state, None)
        if color is None:
            color = self._colors.get(WidgetStates.NORMAL)

        return font, color

    def render(
        self,
        typewriter: TypeWriter,
        state: States,
        text: str,
        bg_color: Color,
        justify: Anchor = LEFT,
        can_be_loc: bool = True,
        wrap: bool = False,
        max_width: int = None
    ) -> Surface:
        """Render a piece of text."""    
        return self._render(typewriter, state, text, bg_color, justify, can_be_loc, wrap, max_width)

    @cache
    def _render(
        self,
        typewriter: TypeWriter,
        state: States,
        text: str,
        bg_color: Color,
        justify: Anchor = LEFT,
        can_be_loc: bool = True,
        wrap: bool = False,
        max_width: int = None
    ) -> Surface:
        """Render a piece of text."""
        font = self._fonts.get(state, None)
        if font is None:
            font = self._fonts.get(WidgetStates.NORMAL)
        color = self._colors.get(state, None)
        if color is None:
            color = self._colors.get(WidgetStates.NORMAL)
        rendered_text = typewriter.render(font, text, color, bg_color, justify, can_be_loc, wrap, max_width)
        return rendered_text

    def cache_clear(self):
        self._render.cache_clear()

class Textual(Graphical):
    
    def __init__(self, art: Art, font: str, color: Color, text_or_loc: str | TextFormatter, justify: Anchor = CENTER, wrap: bool = False, **kwargs) -> None:
        super().__init__(art=art, **kwargs)
        self._fonts = Fonts(font, color)
        self.text = text_or_loc
        self._justify = justify
        self.state = WidgetStates.NORMAL
        self.wrap = wrap

    def set_text_or_loc(self, new_text_or_loc: str | TextFormatter):
        """Reset the text or loc to a new value."""
        self._text = new_text_or_loc
        self.notify_change()

    def finish(self):
        super().finish()
        self._fonts.cache_clear()

    def _render_text(self, typewriter: TypeWriter):
        return self._fonts.render(
            typewriter,
            self.state,
            self.text,
            None,
            self._justify,
            True,
            self.wrap,
            self.width
        )

    def _render_text_on_bg(self, settings: Settings, typewriter: TypeWriter):
        """Return the surface of the Label."""
        bg = self._arts.get(self.state, **settings).copy()
        rendered_text = self._render_text(typewriter)
        text_width, text_height = rendered_text.get_size()
        just_x = self._justify[0]*(bg.get_width() - text_width)
        just_y = self._justify[1]*(bg.get_height() - text_height)
        bg.blit(rendered_text, (just_x, just_y))
        return bg
