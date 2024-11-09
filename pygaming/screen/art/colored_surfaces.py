"""The colored_surface module contains the ColoredSurface class which is a pygame Surface."""

from typing import Union, Sequence
from pygame import Surface, SRCALPHA, draw
from ...color import Color
from .art import Art
from .art import Transformation


ColorLike = Union[Color, tuple[int, int, int], tuple[int, int, int, int]]

class ColoredRectangle(Art):
    """A ColoredRectangle is a Surface with only one color."""

    def __init__(
        self,
        color: ColorLike,
        width: int,
        height: int,
        thickness: int = 0,
        border_radius: int = -1,
        border_top_left_radius: int = -1,
        border_top_right_radius: int = -1,
        border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1,
        transformation: Transformation = None
    ):
        """Create a rectangle"""
        super().__init__(transformation)

        self.color = color
        self._width = width
        self._height = height
        self.thickness = thickness
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius
        self._find_initial_dimension()

    def _load(self):
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.rect(surf, self.color, (0, 0, self._width, self._height), self.thickness, self.border_radius,
                  self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
        self.surfaces = (surf,)
        self.durations = (0,)

class ColoredCircle(Art):
    """A ColoredCircle is a Surface with a colored circle at the center of it."""

    def __init__(
        self,
        color: ColorLike,
        radius: int,
        thickness: int = 0,
        draw_top_right: bool = False,
        draw_top_left: bool = False,
        draw_bottom_left: bool = False,
        draw_bottom_right: bool = False,
        transformation: Transformation = None
    ):
        super().__init__(transformation)
        self.radius = radius
        self.color = color
        self.thickness = thickness
        self.draw_top_right = draw_top_right
        self.draw_top_left = draw_top_left
        self.draw_bottom_left = draw_bottom_left
        self.draw_bottom_right = draw_bottom_right
        self._height = 2*radius
        self._width = 2*radius
        self._find_initial_dimension()
    
    def _load(self):
        surf = Surface((self.radius*2, self.radius*2), SRCALPHA)
        draw.circle(surf, self.color, (self.radius, self.radius),
            self.radius, self.thickness, self.draw_top_right, self.draw_top_left, self.draw_bottom_left, self.draw_bottom_right)
    
        self.surfaces = (surf,)
        self.durations = (0,)

class ColoredPolygon(Art):

    def __init__(
        self,
        color: ColorLike,
        points: Sequence[tuple[int, int]],
        thickness: int = 0
    ):
        self.points = points
        self.thickness = thickness
        self.color = color

        self._height = max(p[1] for p in self.points)
        self._width = max(p[0] for p in self.points)
        self._find_initial_dimension()
    
    def _load(self):
        
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.polygon(surf, self.color, self.points, self.thickness)

        self.surfaces = (surf,)
        self.durations = (0,)