from typing import Tuple
from pygame.font import Font as Ft
from pygame import Color
from pygame.surface import Surface

class Font(Ft):

    def __init__(self, name: str | None, size: int, color: Color, settings, bold: bool = False, italic: bool = False, underline: bool = False) -> None:
        super().__init__(name, size)
        self.name = name
        self.color = color
        self.set_bold(bold)
        self.set_italic(italic)
        self.set_underline(underline)
        self._settings = settings

    def render(self, text: str) -> Surface:
        return super().render(text, self._settings.antialias, self.color)

    def set_color(self, color: Color):
        self.color = color
    
    