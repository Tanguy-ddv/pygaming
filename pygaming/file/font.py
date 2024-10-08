"""Font files represent the file of a font."""
import pygame

from .file import File, get_file
from ..font import Font

class FontFile(File):
    """Represent the file of a font stored in the assets/font folder."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.full_path = get_file(folder='fonts', file=name)

    #pylint: disable=arguments-differ
    def get(
            self,
            size: int,
            color: pygame.Color,
            settings,
            italic: bool = False,
            bold: bool = False,
            underline: bool = False
        ) -> pygame.font.Font:
        """
        Get the font
        
        Params:
        ----
        - size: int, the size of the font.
        - color: pygame.Color: the color of the Font
        - settings: Settings, the self.settings of the Game
        - italic: bool, flag for the font
        - bold: bool, flage for the font
        - underline: bool, flags for the font.
        """
        return Font(self.full_path, size, color, settings, bold, italic, underline)

default_font = FontFile("")
default_font.full_path = None
