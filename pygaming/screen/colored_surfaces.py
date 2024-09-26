"""The colored_surface module contains the ColoredSurface class which is a pygame Surface."""

from typing import Union
from pygame import Surface, Color, SRCALPHA
from pygame.color import THECOLORS
import pygame

ColorLike = Union[str, Color, tuple[int, int, int], tuple[int, int, int, int]]

def _get_color(color: ColorLike):
    """Get the pygame.Color instance with a ColorLike object."""
    if isinstance(color, str): # Translate the string into a color
        if color in THECOLORS:
            color = THECOLORS[color]
        elif color.startswith('#'):
            color = Color(color)
        else:
            print(f"'{color}' is not a color, replaced by white.")
            color = Color(255,255,255,255)
    return color


class ColoredRectangle(Surface):
    """A ColoredRectangle is a Surface with only one color."""

    def __init__(self, color: ColorLike, width: int, height: int):
        super().__init__((width, height), SRCALPHA)

        color = _get_color(color)
        self.fill(color)

class ColoredRoundedRectangle(Surface):
    """A ColoredRoundedRectangle is a Surface with one rounded rectangle in the middle."""

    def __init__(self, color: ColorLike, width: int, height: int, border_radius: int):

        super().__init__((width, height), SRCALPHA)
        self.fill((0, 0, 0, 0))
        color = _get_color(color)
        pygame.draw.rect(self, color, (0,0, width, height), 0, border_radius)
    
class ColoredCircle(Surface):
    """A ColoredCircle is a Surface with a colored circle at the center of it."""

    def __init__(self, color: ColorLike, radius: int):
        super().__init__((radius*2, radius*2), SRCALPHA)
        color = _get_color(color)
        pygame.draw.circle(self, color, (radius, radius), radius)