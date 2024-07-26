from pygame.font import Font as Ft
from pygame import Color
from pygame.surface import Surface

class Font(Ft):

    def __init__(self, name: str | None, size: int, color: Color, bold: bool = False, italic: bool = False, underline: bool = False, antialias: bool = True) -> None:
        super().__init__(name, size)
        self.name = name
        self.color = color
        self.set_bold(bold)
        self.set_italic(italic)
        self.set_underline(underline)
        self.antialias = antialias

    def render(self, text: str) -> Surface:
        return super().render(text, self.antialias, self.color)

    def set_color(self, color: Color):
        self.color = color
    
    def set_antialias(self, antialias: bool):
        self.antialias = antialias