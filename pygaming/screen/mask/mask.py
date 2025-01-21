"""This mask submodule contains the bases for masks and geometrical masks."""

from abc import ABC, abstractmethod
from typing import Callable
import numpy as np
import cv2
from pygame import Surface, surfarray as sa, SRCALPHA, draw, Rect
from ...error import PygamingException
from ...settings import Settings

# Mask effects
ALPHA = 'alpha'
DARKEN = 'darken'
LIGHTEN = 'lighten'
SATURATE = 'saturate'
DESATURATE = 'desaturate'

_EFFECT_LIST = [ALPHA, DARKEN, LIGHTEN, SATURATE, DESATURATE]

class Mask(ABC):
    """Mask is an abstract class for all masks."""

    def __init__(self, width: int, height: int) -> None:
        super().__init__()
        self._loaded = False
        self._width = width
        self._height = height
        self.matrix: np.ndarray = None
        self.settings = None

    @property
    def width(self):
        """The width of the mask."""
        return self._width

    @property
    def height(self):
        """The height of the mask."""
        return self._height

    @abstractmethod
    def _load(self, settings: Settings):
        raise NotImplementedError()

    def load(self, settings: Settings):
        """Load the mask."""
        self.settings = settings
        self._load(settings)
        self._loaded = True

    def unload(self):
        """Unload the mask."""
        self.matrix = None
        self._loaded = False

    def update(self, loop_duration):
        """Update the mask if it can be updated."""

    def is_loaded(self):
        """Return True if the mask is loaded, False otherwise."""
        return self._loaded

    def get_size(self) -> tuple[int, int]:
        """Return the size of the mask"""
        return (self.width, self.height)

    def apply(self, surface: Surface, effects: dict[str, float]):
        """Apply the mask to an image."""
        if not self._loaded:
            self.load(self.settings)

        if surface.get_size() != (self._width, self._height):
            raise PygamingException("The size of the mask do not match the size of the art.")

        if not effects:
            return

        if ALPHA in effects:
            surf_alpha = sa.array_alpha(surface)
            surf_alpha[:] = np.astype(np.clip(surf_alpha * self.matrix * effects[ALPHA]/100, 0, 255), surf_alpha.dtype)

        if any(effect in _EFFECT_LIST for effect in effects):
            rgb_array = sa.pixels3d(surface)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)

            if DARKEN in effects:
                hls_array[:,:, 1] = hls_array[:,:, 1] * (1 - self.matrix * effects[DARKEN]/100)

            elif LIGHTEN in effects:
                hls_array[:,:, 1] = 255 - (255 - hls_array[:,:, 1]) * (1 - self.matrix * effects[LIGHTEN]/100)

            if DESATURATE in effects:
                hls_array[:,:, 2] = hls_array[:,:, 2] * (1 - self.matrix * effects[DESATURATE]/100)

            elif SATURATE in effects:
                hls_array[:,:, 2] = 255 - (255 - hls_array[:,:, 2]) * (1 - self.matrix * effects[SATURATE]/100)

            rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[:].astype(rgb_array.dtype)

    def __bool__(self):
        return True

    def get_at(self, pos: tuple[int, int]):
        """
        Return the value of the matrix at this coordinate.
        """
        if not self.is_loaded():
            self.load(self.settings)
        return not bool(self.matrix[int(pos[0]), int(pos[1])])

    def set_at(self, pos: tuple[int, int], value: float):
        """
        Set a new value for the matrix at this coordinate.
        """
        if not self.is_loaded():
            self.load(self.settings)
        self.matrix[pos] = min(1, max(0, value))

    def not_null_columns(self):
        """Return the list of indices of the columns that have at least one value different from 0."""
        if not self.is_loaded():
            self.load(self.settings)
        return np.where(self.matrix.any(axis=0))[0]

    def not_null_rows(self):
        """Return the list of indices of the rows that have at least one value different from 0."""
        if not self.is_loaded():
            self.load(self.settings)
        return np.where(self.matrix.any(axis=1))[0]

    def is_empty(self):
        """Return True if all the pixels in the mask are set to 0."""
        if not self.is_loaded():
            self.load(self.settings)
        return np.sum(self.matrix) == 0

    def is_full(self):
        """Return True if all the pixels in the mask are set to 1."""
        if not self.is_loaded():
            self.load(self.settings)
        return np.sum(self.matrix) == self.height*self.width

class MatrixMask(Mask):
    """A matrix mask is a mask based on a matrix."""

    def __init__(self, width: int, height: int, matrix: np.ndarray) -> None:
        super().__init__(width, height)
        self.matrix = np.clip(matrix, 0, 1)

    def unload(self):
        """Don't do anything as we want to keep the matrix."""

    def _load(self, settings: Settings):
        """Don't do anything as the matrix is already loaded."""

class FreeMask(Mask):
    """A FreeMask is a mask whose matrix can be freely and explicitly change during the game."""

    def __init__(self, width, height, initial_matrix):
        super().__init__(width, height)
        self.__initial_matrix = initial_matrix

    def _load(self, settings):
        self.matrix = self.__initial_matrix

    def update_matrix(self, new_matrix: np.ndarray):
        """Update the current matrix with a user-defined matrix. Both matrices should have the same shape."""
        if self.matrix.shape == new_matrix.shape:
            self.matrix = new_matrix
        else:
            raise ValueError(f"The matrices have two different shapes: {self.matrix.shape}, {new_matrix.shape}")

class Circle(Mask):
    """A Circle is a mask with two values: 0 in the circle and 1 outside."""

    def __init__(self, width: int, height: int, radius: float, center: tuple[int, int] = None):
        super().__init__(width, height)
        self.radius = radius
        if center is None:
            center = width/2 - 0.5, height/2 - 0.5
        self.center = center

    def _load(self, settings: Settings):
        grid_x, grid_y = np.ogrid[:self._width, :self._height]
        distances = np.sqrt((grid_x - self.center[0]) ** 2 + (grid_y - self.center[1]) ** 2)
        self.matrix = (distances > self.radius).astype(int)

class Ellipse(Mask):
    """An Ellipsis is a mask with two values: 0 in the ellipsis and 1 outside."""

    def __init__(self, width: int, height: int, x_radius: int, y_radius: int, center: tuple[int, int] = None):
        super().__init__(width, height)
        self.x_radius = x_radius
        self.y_radius = y_radius
        if center is None:
            center = width/2 - 0.5, height/2 - 0.5
        self.center = center

    def _load(self, settings: Settings):
        grid_y, grid_x = np.ogrid[:self._height, :self._width]
        distances = np.sqrt((grid_x - self.center[0]) ** 2 / self.x_radius**2 + (grid_y - self.center[1]) ** 2 / self.y_radius**2)
        self.matrix = (distances > 1).astype(int)

class Rectangle(Mask):
    """A Rectangle is a mask with two values: 0 inside the rectangle and 1 outside."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int):
        """
        A Rectangle is a mask with two values: 0 inside the rectangle and 1 outside.
        
        Params:
        ----
        - width: int, the width of the mask.
        - height: int, the height of the mask.
        - left: int, the coordinate of the left of the rectangle, included.
        - top: int, the coordinate of the top of the rectangle, included.
        - right: int, the coordinate of the right of the rectangle, included.
        - bottom: int, the coordinate of the bottom of the rectangle, included.

        Example:
        ----
        >>> r = Rectangle(6, 4, 2, 1, 4, 5)
        >>> r.load(settings)
        >>> print(r.matrix)
        >>> [[1 1 1 1 1 1]
             [1 1 0 0 0 1]
             [1 1 0 0 0 1]
             [1 1 1 1 1 1]]
        """

        super().__init__(width, height)
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def _load(self, settings: Settings):
        grid_y, grid_x = np.ogrid[:self._height, :self._width]
        self.matrix = 1 - ((self.left <= grid_x) & (grid_x <= self.right) & (self.top <= grid_y) & (grid_y <= self.bottom)).astype(int)

class Polygon(Mask):
    """
    A Polygon is a mask with two values: 0 inside the polygon and 1 outside the polygon.
    The Polygon is defined from a list of points. If points are outside of [0, width] x [0, height],
    the polygon is cropped.
    """

    def __init__(self, width: int, height: int, points: list[tuple[int, int]]) -> None:
        super().__init__(width, height)

        self.points = points

    def _load(self, settings: Settings):
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.polygon(surf, (0, 0, 0, 255), self.points)
        self.matrix = 1 - sa.array_alpha(surf)/255

class RoundedRectangle(Mask):
    """A RoundedRectangle mask is a mask with two values: 0 inside of the rectangle with rounded vertexes, and 1 outside."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int, radius: int):
        super().__init__(width, height)
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.radius = radius

    def _load(self, settings: Settings):
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.rect(surf, (0, 0, 0, 255), Rect(self.left, self.top, self.right - self.left, self.bottom - self.top), 0, self.radius)
        self.matrix = 1 - sa.array_alpha(surf)/255

class GradientCircle(Mask):
    """
    A GradientCircle mask is a mask where the values ranges from 0 to 1. All pixels in the inner circle are set to 0,
    all pixels out of the outer cirlce are set to 1, and pixels in between have an intermediate value.

    The intermediate value is defined by the transition function. This function must be vectorized.
    """

    def __init__(
            self,
            width: int,
            height: int,
            inner_radius: int,
            outer_radius: int,
            transition: Callable[[float], float] = lambda x:x,
            center: tuple[int, int] = None
        ):
        super().__init__(width, height)
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.transition = transition

        if center is None:
            center = width/2 - 0.5, height/2 - 0.5
        self.center = center

    def _load(self, settings: Settings):
        grid_x, grid_y = np.ogrid[:self._width, :self._height]
        distances = np.sqrt((grid_x - self.center[0]) ** 2 + (grid_y - self.center[1]) ** 2)
        self.matrix = np.clip((distances - self.inner_radius)/(self.outer_radius - self.inner_radius), 0, 1)
        self.matrix = self.transition(self.matrix)

class GradientRectangle(Mask):
    """
    A GradientRectangle mask is a mask where values range from 0 to 1. All pixels inside the inner rectangle are set to 0.
    All pixels outside the outer rectangle are set to 1. All pixels in between have an intermediate value.

    The intermediate value is defined by the transition function.
    """

    def __init__(
        self,
        width: int,
        height: int,
        inner_left: int,
        inner_right: int,
        inner_top: int,
        inner_bottom: int,
        outer_left: int = None,
        outer_right: int = None,
        outer_top: int = None,
        outer_bottom: int = None,
        transition: Callable[[float], float] = lambda x:x,
    ):

        super().__init__(width, height)

        if outer_left is None:
            outer_left = 0
        if outer_right is None:
            outer_right = width - 1
        if outer_top is None:
            outer_top = 0
        if outer_bottom is None:
            outer_bottom = height - 1


        if outer_bottom < inner_bottom or outer_top > inner_top or outer_left > inner_left or outer_right < inner_right:
            raise ValueError(
                f"""The outer rectangle cannot be inside of the inner rectangle, got
                inner = ({inner_left, inner_right, inner_top, inner_bottom})
                and outer = ({outer_left, outer_right, outer_top, outer_bottom})"""
            )

        self.inner_left = inner_left
        self.inner_right = inner_right
        self.inner_bottom = inner_bottom
        self.inner_top = inner_top

        self.outer_left = outer_left
        self.outer_right = outer_right
        self.outer_bottom = outer_bottom
        self.outer_top = outer_top

        self.transition = transition

    def _load(self, settings: Settings):
        y_indices, x_indices = np.meshgrid(np.arange(self.height), np.arange(self.width), indexing='ij')

        left_dist = np.clip((self.inner_left - x_indices) / (self.inner_left - self.outer_left + 1), 0, 1)
        right_dist = np.clip((x_indices - self.inner_right) / (self.outer_right - self.inner_right + 1), 0, 1)
        top_dist = np.clip((self.inner_top - y_indices) / (self.inner_top - self.outer_top + 1), 0, 1)
        bottom_dist = np.clip((y_indices - self.inner_bottom) / (self.outer_bottom - self.inner_bottom + 1), 0, 1)

        self.matrix = self.transition(np.clip(np.sqrt(left_dist**2 + right_dist**2 + top_dist**2 + bottom_dist**2), 0, 1))
