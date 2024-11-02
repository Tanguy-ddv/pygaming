"""The Font module contain the font class."""
from pygame.font import Font as Ft
from pygame import Surface
from ..screen.colored_surfaces import ColoredRectangle
from ..color import Color
from .texts import Texts
from .database import Database
from ..settings import Settings
from ..file import get_file

class Font(Ft):
    """The Font class is used to display texts."""

    def __init__(
        self,
        path: str | None,
        size: int,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False
    ) -> None:
        """
        Create a Font instance.

        Params:
        ----
        name: the path to the font in the assets/font folder.
        size: the size of the font
        color: the color of the font
        settings: the self.settings of the game. It is used to 
        bold, italic, underline: flags for the font.
        """
        super().__init__(path, size)
        self.name = path
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough

class TypeWriter:
    """The TypeWriter is a class used to manage the fonts and the text generation."""

    def __init__(self, database: Database, settings: Settings, phase_name: str) -> None:

        self._settings = settings
        self._db = database
        fonts = database.get_fonts(phase_name)
        self._fonts: dict[str, Font] = {
            font_name : Font(get_file('fonts', path, True), size, bold, italic, underline)
            for (font_name, (path, size, bold, italic, underline)) 
            in fonts
        }

        self._phase_name = phase_name
        self._texts = Texts(database, settings, phase_name)

        self._default_font = Ft(None, 15)
        self._default_font.get_descent()
    
    def update_settings(self):
        """Update the texts based on the new language."""
        self._texts = Texts(self._db, self._settings, self._phase_name)
    
    def _get_font(self, font):
        """Get the font from the dict or return the default font"""
        if font in self._fonts:
            return self._fonts[font]
        else:
            return self._default_font

    def render(self, font: str, text_or_loc: str, color: Color, background_color: Color = None) -> Surface:
        """Draw text or localization on a new Surface."""
        thefont = self._get_font(font)
        if "\n" in text_or_loc:
            lines = [line.strip() for line in text_or_loc.split('\n')]
            line_size = thefont.get_linesize()
            line_spacing = line_size//20 + 1
            bg_width = max(thefont.size(line)[0] for line in lines)
            bg_height = len(lines)*line_size + line_spacing*(len(lines) - 1)
            background = ColoredRectangle(Color(0, 0, 0, 0) if background_color is None else background_color, bg_width, bg_height)
            line_y = 0
            for line in lines:
                render = thefont.render(line, self._settings.antialias, color, background_color)
                background.blit(render, (0, line_y))
                line_y += line_spacing + line_size
            return background

        return thefont.render(self._texts.get(text_or_loc), self._settings.antialias, color, background_color)


    def size(self, font: str, text_or_loc: str) -> tuple[int, int]:
        """
        Returns the dimensions needed to render the text. This can be used to help determine the positioning needed for text before it is rendered.
        It can also be used for word wrapping and other layout effects.

        Be aware that most fonts use kerning which adjusts the widths for specific letter pairs.
        For example, the width for "ae" will not always match the width for "a" + "e".
        """
        if "\n" in text_or_loc:
            lines = [line.strip() for line in text_or_loc.split('\n')]
            thefont = self._get_font(font)
            line_size = thefont.get_linesize()
            line_spacing = line_size//20 + 1
            bg_width = max(thefont.size(line)[0] for line in lines)
            bg_height = len(lines)*line_size + line_spacing*(len(lines) - 1)
            return bg_width, bg_height
        
        return self._get_font(font).size(self._texts.get(text_or_loc))

    def get_ascent(self, font: str):
        """Return the height in pixels for the font ascent.
        The ascent is the number of pixels from the font baseline to the top of the font."""
        return self._get_font(font).get_ascent()

    def get_descent(self, font: str):
        """Return the height in pixels for the font descent.
        The descent is the number of pixels from the font baseline to the bottom of the font."""
        return self._get_font(font).get_descent()

    def get_linesize(self, font: str):
        """
        Return the height in pixels for a line of text with the font.
        When rendering multiple lines of text this is the recommended amount of space between lines.
        """
        return self._get_font(font).get_linesize()