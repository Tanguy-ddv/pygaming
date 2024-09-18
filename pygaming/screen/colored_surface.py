"""The colored_surface module contains the ColoredSurface class which is a pygame Surface."""

from typing import Union
from pygame import Surface, Color, SRCALPHA
from pygame.color import THECOLORS

ColorLike = Union[str, Color, tuple[int, int, int], tuple[int, int, int, int]]

class ColoredSurface(Surface):
    """A ColoredSurface is a Surface with only one color."""

    def __init__(self, color: ColorLike, width: int, height: int):
        super().__init__((width, height), SRCALPHA)

        if isinstance(color, str): # Translate the string into a color
            if color in THECOLORS:
                color = THECOLORS[color]
            elif color.startswith('#'):
                color = Color(color)
            else:
                print(f"'{color}' is not a color, replaced by white.")
                color = Color(255,255,255,255)

        self.fill(color)
