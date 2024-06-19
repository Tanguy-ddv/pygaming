from .file import File
from .._utils import get_file
import pygame

class FontFile(File):
    """Represent the file of a font."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        if name.endswith('.ttf'):
            self.full_path = get_file(folder='assets/fonts', path=name)
        else:
            self.full_path = get_file(folder='assets/fonts', path=name + '.ttf')

    def get(self, size: int, italic: bool = False, bold: bool = False, underline: bool = False) -> pygame.font.Font:
        font = pygame.font.Font(self.full_path, size)
        font.set_italic(italic)
        font.set_bold(bold)
        font.set_underline(underline)
        return font