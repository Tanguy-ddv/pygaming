"""The Font module contain the font class."""
from pygame.font import Font as Ft
from pygame import Color
from pygame import Surface

class Font(Ft):
    """The Font class is used to display texts."""

    def __init__(
        self,
        name: str | None,
        size: int,
        color: Color,
        settings = None, # No typing to avoid circular imports
        bold: bool = False,
        italic: bool = False,
        underline: bool = False
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
        super().__init__(name, size)
        self.name = name
        self.color = color
        self.set_bold(bold)
        self.set_italic(italic)
        self.set_underline(underline)
        self._settings = settings

    def render(self, text: str) -> Surface:
        """Create a surface from the font by writing a text."""
        if self._settings is None:
            antialias = False
        else:
            antialias = self._settings.antialias
        return super().render(text, antialias, self.color)

    def set_color(self, color: Color):
        """Change the color of the font."""
        self.color = color
