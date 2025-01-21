"""The Font module contain the font class."""
from pygame.font import Font as _Ft
from pygame import Surface, SRCALPHA, Rect
from ..color import Color
from .texts import Texts, TextFormatter
from .database import Database
from ..settings import Settings
from ..file import get_file
from ..screen.anchors import TOP_LEFT

class Font(_Ft):
    """The Font class is used to display texts."""

    def __init__(
        self,
        name: str | None,
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
        super().__init__(name, size)
        self.name = name
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough

class TypeWriter:
    """The TypeWriter is a class used to manage the fonts and the text generation."""

    def __init__(self, database: Database, settings: Settings, first_phase: str) -> None:

        self._db = database
        self._all_phases_fonts: dict[str, Font] = {
            font_name : Font(get_file('fonts', path) if path != "default" else None, size, bold, italic, underline, strikethrough)
            for (font_name, (path, size, italic, bold, underline, strikethrough)) 
            in database.get_fonts(first_phase).items()
        }
        self._this_phase_fonts:  dict[str, Font] = {
            font_name : Font(get_file('fonts', path) if path != "default" else None, size, bold, italic, underline, strikethrough)
            for (font_name, (path, size, italic, bold, underline, strikethrough)) 
            in database.get_fonts('all').items()
        }

        self._current_phase = first_phase
        self._texts = Texts(database, settings, first_phase)

        self._default_font = Font(None, 15)
        self._antialias = False

    def update_settings(self, settings: Settings, phase):
        """Update the texts based on the new language."""
        self._texts.update(settings, phase)
        if self._current_phase != phase: # If we change the phase, we change the fonts
            self._this_phase_fonts:  dict[str, Font] = {
            font_name : Font(get_file('fonts', path) if path != "default" else None, size, bold, italic, underline, strikethrough)
            for (font_name, (path, size, italic, bold, underline, strikethrough)) 
            in self._db.get_fonts('all').items()
        }
        self._antialias = settings.antialias

    def _get_font(self, font: str) -> Font:
        """Get the font from the dict or return the default font"""
        thefont = self._this_phase_fonts.get(font, None)
        if thefont is None:
            thefont = self._all_phases_fonts.get(font, self._default_font)
        return thefont

    def render(self, font: str, text_or_loc: str | TextFormatter, color: Color, background_color: Color = None, justify: tuple[float, float] = TOP_LEFT) -> Surface:
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
        the surface returned has a solid background with this color, otherwise the background is transparent
        - justify: tuple[float, float] Only for multiline renders, justifies justify the text according to its first component.
        """
        thefont = self._get_font(font)
        thetext = self._texts.get(text_or_loc)
        if "\n" in thetext:
            lines = [line.strip() for line in text_or_loc.split('\n')]
            line_size = thefont.get_linesize()
            bg_width = max(thefont.size(line)[0] for line in lines)
            bg_height = len(lines)*line_size
            background = Surface((bg_width, bg_height), SRCALPHA)
            background.fill((0, 0, 0, 0) if background_color is None else background_color)
            line_y = 0
            for line in lines:
                render = thefont.render(line, self._antialias, color, background_color)
                background.blit(render, ((bg_width - render.get_width())*justify[0], line_y))
                line_y += line_size
            return background

        return thefont.render(thetext, self._antialias, color, background_color)

    def render_paragraphs(self, font: str, text_or_loc: str | TextFormatter, color: Color, rect: Rect, background_color: Color = None) -> Surface:
        """
        Draw a text or a localization as multiple justified paragraphs.
        
        Params:
        ----
        - font: str, the name of the font. If the name is not find (which means it is not present on the fonts.sql file for this phase),
        use the default system font with a size of 20
        - text_or_loc: str, the text to be rendered. If it is recognized as a loc, the text in the current language is displayed, else.
        Otherwise, the test itself is used.
        - color: Color, the color to display the font in
        - background_color: Color = None, the color of the background. If a color is given,
        the surface returned has a solid background with this color, otherwise the background is transparent
        """
        thefont = self._get_font(font)
        thetext = self._texts.get(text_or_loc)

        if thefont.size(thetext)[0] <= rect.size[0] and not '\n' in thetext:
            return thefont.render(thetext, True, color, background_color)

        background = Surface(rect.size, SRCALPHA)
        if background_color:
            background.fill((0, 0, 0, 0) if background_color is None else background_color)
        line_size = thefont.get_linesize()
        line_y = 0
        # Render the paragraphs one by one
        for text in thetext.split('\n'):
            words = text.split()
            first_line = True
            while words and line_y <= rect.size[1]:
                thisline = []
                # Find the words that will fit in the line
                while words and thefont.size(('    ' if first_line else '') + ' '.join(thisline + [words[0]]))[0] <= rect.size[0]:
                    thisline.append(words.pop(0))
                if first_line:
                    thisline.insert(0, '   ')

                if words:
                    # Spread the extra pixels among all spaces
                    extra_pixels = rect.size[0] - thefont.size(' '.join(thisline))[0]
                    spaces = [extra_pixels//(len(thisline) - 1) for _ in range(len(thisline) - 1)]
                    if len(thisline) > 1:
                        for i in range(extra_pixels%(len(thisline) - 1)):
                            spaces[i] += 1
                    # Render the line
                    spaces.append(0)
                    word_x = 0
                    for word, space in zip(thisline, spaces):
                        rendered_word = thefont.render(word + ' ', True, color, background_color)
                        background.blit(rendered_word, (word_x, line_y))
                        word_x += thefont.size(word + ' ')[0] + space

                else:
                    # Render the last line
                    rendered_word = thefont.render(' '.join(thisline), True, color, background_color)
                    background.blit(rendered_word, (0, line_y))

                line_y += line_size
                first_line = False

        return background

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
