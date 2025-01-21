"""The colored_surface module contains the ColoredSurface class which is a pygame Surface."""

from typing import Sequence
from pygame import Surface, SRCALPHA, draw, gfxdraw, mask as msk
from ...color import ColorLike
from .art import Art
from ...settings import Settings
from .transformation import Transformation

class ColoredRectangle(Art):
    """A ColoredRectangle is an Art with only one color."""

    def __init__(
        self,
        color: ColorLike,
        width: int,
        height: int,
        thickness: int = 0,
        border_radius: int = 0,
        border_top_left_radius: int = -1,
        border_top_right_radius: int = -1,
        border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ):
        """Create a rectangle"""
        super().__init__(transformation, force_load_on_start, permanent)

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

    def _load(self, settings: Settings):
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.rect(surf, self.color, (0, 0, self._width, self._height), self.thickness, self.border_radius,
                  self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius
        )
        self.surfaces = (surf,)
        self.durations = (0,)

class ColoredCircle(Art):
    """A ColoredCircle is an Art with a colored circle at the center of it."""

    def __init__(
        self,
        color: ColorLike,
        radius: int,
        thickness: int = 0,
        draw_top_right: bool = False,
        draw_top_left: bool = False,
        draw_bottom_left: bool = False,
        draw_bottom_right: bool = False,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ):
        super().__init__(transformation, force_load_on_start, permanent)
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

    def _load(self, settings: Settings):
        surf = Surface((self.radius*2, self.radius*2), SRCALPHA)
        draw.circle(surf, self.color, (self.radius, self.radius),
            self.radius, self.thickness, self.draw_top_right, self.draw_top_left, self.draw_bottom_left, self.draw_bottom_right)

        self.surfaces = (surf,)
        self.durations = (0,)

class ColoredEllipse(Art):
    """A ColoredEllipse is an Art with a colored ellipsis at the center."""

    def __init__(self, color: ColorLike, horizontal_radius: int, vertical_radius: int,
            thickness: int = 0, transformation: Transformation = None, force_load_on_start: bool = False, permanent: bool = False) -> None:
        self.color = color
        self.rect = (0, 0, horizontal_radius*2, vertical_radius*2)
        self.thickness = thickness
        super().__init__(transformation, force_load_on_start, permanent)
        self._height = vertical_radius*2
        self._width = horizontal_radius*2
        self._find_initial_dimension()

    def _load(self, settings: Settings):
        surf = Surface(self.rect[2:4], SRCALPHA)
        draw.ellipse(surf, self.color, self.rect, self.thickness)
        self.surfaces = (surf,)
        self.durations = (0,)

class ColoredPolygon(Art):
    """A ColoredEllips is an Art with a colored polygon at the center."""

    def __init__(
        self,
        color: ColorLike,
        points: Sequence[tuple[int, int]],
        thickness: int = 0,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ):
        for p in points:
            if p[0] < 0 or p[1] < 0:
                raise ValueError(f"All points coordinates of a polygon must have a positive value, got {p}")

        self.points = points
        self.thickness = thickness
        self.color = color
        super().__init__(transformation, force_load_on_start, permanent)

        self._height = max(p[1] for p in self.points) + max(0, (thickness-1)//2)
        self._width = max(p[0] for p in self.points) + max(0, (thickness-1)//2)
        self._find_initial_dimension()

    def _load(self, settings: Settings):

        surf = Surface((self._width, self._height), SRCALPHA)
        draw.polygon(surf, self.color, self.points, self.thickness)

        self.surfaces = (surf,)
        self.durations = (0,)

class TexturedPolygon(Art):
    """A Textured polygon is a polygon filled with an art as texture."""

    def __init__(
        self,
        points: Sequence[tuple[int, int]],
        texture: Art,
        texture_top_left: tuple[int, int] = (0, 0),
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ):
        for p in points:
            if p[0] < 0 or p[1] < 0:
                raise ValueError(f"All points coordinates of a polygon must have a positive value, got {p}")
  
        self.points = points
        super().__init__(transformation, force_load_on_start, permanent)

        self._height = max(p[1] for p in self.points)
        self._width = max(p[0] for p in self.points)
        self._find_initial_dimension()

        self.texture = texture
        self.texture_top_left = texture_top_left

    def _load(self, settings: Settings):

        surfaces = []
        need_to_unload = False

        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load()

        for surf in self.texture.surfaces:
            background = Surface((self._width, self._height), SRCALPHA)
            gfxdraw.textured_polygon(background, self.points, surf, *self.texture_top_left)
            surfaces.append(background)

        self.surfaces = tuple(surfaces)
        self.durations = self.texture.durations
        self.introduction = self.texture.introduction

        if need_to_unload:
            self.texture.unload()

class TexturedCircle(Art):
    """A TexturedCircle is an Art with a textured circle at the center of it."""

    def __init__(
        self,
        radius: int,
        texture: Art,
        center: tuple[int, int] = None,
        draw_top_right: bool = False,
        draw_top_left: bool = False,
        draw_bottom_left: bool = False,
        draw_bottom_right: bool = False,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ):
        super().__init__(transformation, force_load_on_start, permanent)
        self.radius = radius
        self.draw_top_right = draw_top_right
        self.draw_top_left = draw_top_left
        self.draw_bottom_left = draw_bottom_left
        self.draw_bottom_right = draw_bottom_right
        if center is None:
            center = texture.width//2, texture.height//2
        self.center = center
        self._width = texture.width
        self._height = texture.height
        self.texture = texture

        self._find_initial_dimension()

    def _load(self, settings: Settings):

        need_to_unload = False
        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load()

        surf = Surface((self._width, self._height), SRCALPHA)
        draw.circle(surf, (255, 255, 255, 255), self.center,
            self.radius, 0, self.draw_top_right, self.draw_top_left, self.draw_bottom_left, self.draw_bottom_right)
        mask = msk.from_surface(surf, 127)
        self.surfaces = (mask.to_surface(setsurface=surface) for surface in self.texture.surfaces)
        self.durations = self.texture.durations

        if need_to_unload:
            self.texture.unload()

class TexturedEllipse(Art):
    """A TexturedEllipse is an Art with a textured ellipsis at the center of it."""

    def __init__(
        self,
        horizontal_radius: int,
        vertical_radius: int,
        texture: Art,
        center: tuple[int, int] = None,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ) -> None:
        super().__init__(transformation, force_load_on_start, permanent)
        if center is None:
            center = texture.width//2, texture.height//2
        self.center = center
        self.rect = (self.center[0] - horizontal_radius, self.center[0] - vertical_radius, horizontal_radius*2, vertical_radius*2)
        self._width = texture.width
        self._height = texture.height
        self.texture = texture
        self._find_initial_dimension()

    def _load(self, settings: Settings):

        need_to_unload = False
        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load()

        surf = Surface(self.rect[2:4], SRCALPHA)
        draw.ellipse(surf, (255, 255, 255, 255), self.rect, 0)
        mask = msk.from_surface(surf, 127)
        self.surfaces = (mask.to_surface(setsurface=surface) for surface in self.texture.surfaces)
        self.durations = self.texture.durations

        if need_to_unload:
            self.texture.unload()

class TexturedRoundedRectangle(Art):
    """A TexturedRoundedRectangle is an Art with rounded angles."""

    def __init__(
        self,
        texture: Art,
        border_radius: int = 0,
        border_top_left_radius: int = -1,
        border_top_right_radius: int = -1,
        border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1,
        transformation: Transformation = None,
        force_load_on_start: bool = False,
        permanent: bool = False
    ):
        super().__init__(transformation, force_load_on_start, permanent)
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

        self._height = texture.height
        self._width = texture.width
        self.texture = texture

        self._find_initial_dimension()

    def _load(self, settings: Settings):

        need_to_unload = False
        if not self.texture.is_loaded:
            need_to_unload = True
            self.texture.load()

        surf = Surface((self.width, self.height), SRCALPHA)
        draw.rect(
            surf,
            (255, 255, 255, 255),
            (0, 0, self.width, self.height),
            0,
            self.border_radius,
            self.border_top_left_radius,
            self.border_top_right_radius,
            self.border_bottom_left_radius,
            self.border_bottom_right_radius
        )
        mask = msk.from_surface(surf, 127)
        self.surfaces = (mask.to_surface(setsurface=surface) for surface in self.texture.surfaces)
        self.durations = self.texture.durations

        if need_to_unload:
            self.texture.unload()
