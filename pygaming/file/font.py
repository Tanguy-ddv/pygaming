from .file import File, get_file
import pygame
from ..font import Font

class FontFile(File):
    """Represent the file of a font."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        if name.endswith('.ttf') or name.endswith('.TTF'):
            self.full_path = get_file(folder='fonts', file=name)
        else:
            self.full_path = get_file(folder='fonts', file=name + '.ttf')

    def get(self, size: int, color: pygame.Color, italic: bool = False, bold: bool = False, underline: bool = False, antialias: bool = True) -> pygame.font.Font:
        return Font(self.full_path, size, color, bold, italic, underline, antialias)

default_font = FontFile("")
default_font.full_path = None