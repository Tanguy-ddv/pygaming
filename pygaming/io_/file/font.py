from .file import File
from ..utils import get_file
import pygame

class FontFile(File):
    """Represent the file of a font."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        if name.endswith('.ttf') or name.endswith('.TTF'):
            self.full_path = get_file(folder='fonts', file=name)
        else:
            self.full_path = get_file(folder='fonts', file=name + '.ttf')

    def get(self, size: int, italic: bool = False, bold: bool = False, underline: bool = False) -> pygame.font.Font:
        font = pygame.font.Font(self.full_path, size)
        font.set_italic(italic)
        font.set_bold(bold)
        font.set_underline(underline)
        return font