"""The Font module contain the font class."""
from pygame.font import Font as _Ft
from pygame import Surface, SRCALPHA
from ..color import Color
from .texts import Texts, TextFormatter
from .database import Database
from ..settings import Settings
from ..file import get_file

class Font(_Ft):
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
        - name: the path to the font in the assets/font folder.
        - size: the size of the font
        - settings: the self.settings of the game. It is used to 
        - bold: bool, flag for the font to be diplayed in bold characters or not
        - italic: bool, flag for the font to be diplayed in italic characters or not
        - underline: bool, flag for the font to be diplayed underlined or not
        - strikethrough: bool, flag for the font to be diplayed with a strikethrough or not
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
            font_name : Font(get_file('fonts', path) if path != "default" else None, size, bold, italic, underline, strikethrough)
            for (font_name, (path, size, italic, bold, underline, strikethrough)) 
            in fonts.items()
        }

        self._phase_name = phase_name
        self._texts = Texts(database, settings, phase_name)

        self._default_font = _Ft(None, 15)
        self._default_font.get_descent()
    
    def update_settings(self):
        """Update the texts based on the new language."""
        self._texts = Texts(self._db, self._settings, self._phase_name)
    
    def _get_font(self, font: str) -> Font:
        """Get the font from the dict or return the default font"""
        if font in self._fonts:
            return self._fonts[font]
        else:
            return self._default_font

    def render(self, font: str, text_or_loc: str | TextFormatter, color: Color, background_color: Color = None) -> Surface:
        """
        Draw text or localization on a new Surface.
        
        Params:
        -----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        - text_or_loc: str, the text to be rendered. If it is recognized as a loc, the text in the current language is displayed, else.
        Otherwise, the test itself is used.
        - color: Color, the color to display the font in
        - background_color: Color = None, the color of the background. If a color is given,
        the surface return has a solid background with this color, otherwise the background is transparent
        """
        thefont = self._get_font(font)
        thetext = self._texts.get(text_or_loc)
        if "\n" in thetext:
            lines = [line.strip() for line in text_or_loc.split('\n')]
            line_size = thefont.get_linesize()
            bg_width = max(thefont.size(line)[0] for line in lines)
            bg_height = len(lines)*line_size
            background = Surface((bg_width, bg_height), SRCALPHA)
            background.fill(Color(0, 0, 0, 0) if background_color is None else background_color)
            line_y = 0
            for line in lines:
                render = thefont.render(line, self._settings.antialias, color, background_color)
                background.blit(render, (0, line_y))
                line_y += line_size
            return background

        return thefont.render(thetext, self._settings.antialias, color, background_color)

    def get_max_size(self, font: str, loc: str):
        """
        Return the dimension of the largest rendered text obtained from the localization in any language.

        Params:
        ----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        - loc: str, the localisation to obtain the longest word with. If this localisation does not exist, return the size
        of the localisation rendered as a text.
        """

        values = self._texts.get_values(loc)
        if not values:
            return self.size(font, loc)            
        max_w = 0
        max_h = 0
        for value in values:
            w, h = self.size(font, value)
            if w > max_w:
                max_w = w
            if h > max_h:
                max_h = h
            return max_w, max_h

    def size(self, font: str, text_or_loc: str | TextFormatter) -> tuple[int, int]:
        """
        Return the dimensions needed to render the text. This can be used to help determine the positioning needed for text before it is rendered.
        It can also be used for word wrapping and other layout effects.

        Be aware that most fonts use kerning which adjusts the widths for specific letter pairs.
        For example, the width for "ae" will not always match the width for "a" + "e".

        Params:
        ----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        - text_or_loc: str, the text to be rendered. If it is recognized as a loc, the text in the current language is displayed, else.
        Otherwise, the test itself is used.
        """
        text = self._texts.get(text_or_loc)
        if "\n" in text:
            lines = [line.strip() for line in text.split('\n')]
            thefont = self._get_font(font)
            line_size = thefont.get_linesize()
            bg_width = max(thefont.size(line)[0] for line in lines)
            bg_height = len(lines)*line_size
            return bg_width, bg_height
        
        return self._get_font(font).size(text)

    def get_ascent(self, font: str):
        """Return the height in pixels for the font ascent.
        The ascent is the number of pixels from the font baseline to the top of the font.
        
        Params:
        ----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        """
        return self._get_font(font).get_ascent()

    def get_descent(self, font: str):
        """Return the height in pixels for the font descent.
        The descent is the number of pixels from the font baseline to the bottom of the font.

        Params:
        ----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        """
        return self._get_font(font).get_descent()

    def get_linesize(self, font: str):
        """
        Return the height in pixels for a line of text with the font.
        When rendering multiple lines of text this is the recommended amount of space between lines.

        Params:
        ----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        """
        return self._get_font(font).get_linesize()