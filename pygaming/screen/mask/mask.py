from abc import ABC, abstractmethod
import numpy as np
from pygame import Surface, surfarray as sa
from ...error import PygamingException
import cv2

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
        self.matrix = None

    @abstractmethod
    def _load(self):
        raise NotImplementedError()
    
    def load(self):
        self._load()
        self._loaded = True

    def unload(self):
        self.matrix = None
        self._loaded = False
    
    def apply(self, surface: Surface, effects: dict[str, float]):
        """Apply the mask to an image."""
        if not self._loaded:
            self.load()
        
        if surface.get_size() != (self._width, self._height):
            raise PygamingException("The size of the mask do not match the size of the art.")
    
        if not len(effects):
            return

        if ALPHA in effects:
            surf_alpha = sa.array_alpha(surface)
            surf_alpha[:] = np.astype(np.clip(surf_alpha * self.matrix * effects[ALPHA], 0, 255), surf_alpha.dtype)

        if any(effect in _EFFECT_LIST for effect in effects):
            rgb_array = sa.pixels3d(surface)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)

            if DARKEN in effects:
                hls_array[:,:, 1] = hls_array[:,:, 1] * (1 - self.matrix * effects[DARKEN]) 
            
            if LIGHTEN in effects:
                hls_array[:,:, 1] = 255 - (255 - hls_array[:,:, 1]) * (1 - self.matrix * effects[LIGHTEN]) 

            if DESATURATE in effects:
                hls_array[:,:, 2] = hls_array[:,:, 2] * (1 - self.matrix * effects[DESATURATE])
            
            if SATURATE in effects:
                hls_array[:,:, 2] = 255 - (255 - hls_array[:,:, 2]) * (1 - self.matrix * effects[SATURATE])

            rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[:]
    
    def __bool__(self):
        return True


class MatrixMask(Mask):
    """A matrix mask is a mask based on a matrix."""
    
    def __init__(self, width: int, height: int, matrix: np.ndarray) -> None:
        super().__init__(width, height)
        self.matrix = np.clip(matrix, 0, 1)

    def unload(self):
        """Don't do anything as we want to keep the matrix."""
    
    def _load(self):
        """Don't do anything as the matrix is already loaded."""

class Circle(Mask):
    """A Circle is a mask with two values: 0 in the circle and 1 outside."""

    def __init__(self, width: int, height: int, radius: float, center: tuple[int, int] = None):
        super().__init__(width, height)
        self.radius = radius
        if center is None:
            center = width/2 - 0.5, height/2 - 0.5
        self.center = center

    def _load(self):
        grid_x, grid_y = np.ogrid[:self._width, :self._height]
        distances = np.sqrt((grid_x - self.center[0]) ** 2 + (grid_y - self.center[1]) ** 2)
        self.matrix = (distances > self.radius).astype(int)

class Ellipsis(Mask):
    """An Ellipsis is a mask with two values: 0 in the ellipsis and 1 outside."""

    def __init__(self, width: int, height: int, x_radius: int, y_radius: int, center: tuple[int, int] = None):
        super().__init__(width, height)
        self.x_radius = x_radius
        self.y_radius = y_radius
        if center is None:
            center = width/2 - 0.5, height/2 - 0.5
        self.center = center
    
    def _load(self):
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

        If a negative number is passed, then count from the end (as any iterable in python)

        Example:
        ----
        >>> r = Rectangle(6, 4, 2, 1, 4, -2)
        >>> r.load()
        >>> print(r.matrix)
        >>> [[1 1 1 1 1 1]
             [1 1 0 0 0 1]
             [1 1 0 0 0 1]
             [1 1 1 1 1 1]]
        """

        super().__init__(width, height)
        self.left = left%self._width
        self.top = top%self._height
        self.right = right%self._width
        self.bottom = bottom%self._height

    def _load(self):
        grid_y, grid_x = np.ogrid[:self._height, :self._width]
        self.matrix = 1 - ((self.left <= grid_x) & (grid_x <= self.right) & (self.top <= grid_y) & (grid_y <= self.bottom)).astype(int)
