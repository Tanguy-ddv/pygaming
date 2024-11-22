from abc import ABC, abstractmethod
import numpy as np
from typing import Callable
from pygame import Surface, surfarray as sa, SRCALPHA, draw, Rect
from ...error import PygamingException
from ...file import get_file
from PIL import Image
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
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    @abstractmethod
    def _load(self):
        raise NotImplementedError()
    
    def load(self):
        self._load()
        self._loaded = True

    def unload(self):
        self.matrix = None
        self._loaded = False
    
    def is_loaded(self):
        return self._loaded
    
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

            elif LIGHTEN in effects:
                hls_array[:,:, 1] = 255 - (255 - hls_array[:,:, 1]) * (1 - self.matrix * effects[LIGHTEN]) 

            if DESATURATE in effects:
                hls_array[:,:, 2] = hls_array[:,:, 2] * (1 - self.matrix * effects[DESATURATE])

            elif SATURATE in effects:
                hls_array[:,:, 2] = 255 - (255 - hls_array[:,:, 2]) * (1 - self.matrix * effects[SATURATE])

            rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[:].astype(rgb_array.dtype)

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

class Polygon(Mask):
    """
    A Polygon is a mask with two values: 0 inside the polygon and 1 outside the polygon.
    The Polygon is defined from a list of points. If points are outside of [0, width] x [0, height],
    the polygon is cropped.
    """

    def __init__(self, width: int, height: int, points: list[tuple[int, int]]) -> None:
        super().__init__(width, height)
        
        self.points = points
    
    def _load(self):
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.polygon(surf, (0, 0, 0, 255), self.points)
        self.matrix = 1 - sa.array_alpha(surf)/255

class RoundedRectangle(Mask):
    """A RoundedRectangle mask is a mask with two values: 0 inside of the rectangle with rounded vertexes, and 1 outside."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int, radius: int):
        super().__init__(width, height)
        self.left = left%self._width
        self.top = top%self._height
        self.right = right%self._width
        self.bottom = bottom%self._height
        self.radius = radius
    
    def _load(self):
        surf = Surface((self._width, self._height), SRCALPHA)
        draw.rect(surf, (0, 0, 0, 255), Rect(self.left, self.top, self.right - self.left, self.bottom - self.top), 0, self.radius)
        self.matrix = 1 - sa.array_alpha(surf)/255

class GradientCircle(Mask):
    """
    A GradientCircle mask is a mask where the values ranges from 0 to 1. All pixels in the inner circle are set to 0,
    all pixels out of the outer cirlce are set to 1, and pixels in between have an intermediate value.

    The intermediate value is defined by the transition function. This function must be vectorized.
    """

    def __init__(self, height: int, width: int, inner_radius: int, outer_radius: int, transition: Callable[[float], float] = lambda x:x, center: tuple[int, int] = None):
        super().__init__(width, height)
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.transition = transition

        if center is None:
            center = width/2 - 0.5, height/2 - 0.5
        self.center = center

    def _load(self):
        grid_x, grid_y = np.ogrid[:self._width, :self._height]
        distances = np.sqrt((grid_x - self.center[0]) ** 2 + (grid_y - self.center[1]) ** 2)
        self.matrix = np.clip((distances - self.inner_radius)/(self.outer_radius - self.inner_radius), 0, 1)
        self.matrix = self.transition(self.matrix)

class FromArtAlpha(Mask):
    """A mask from the alpha layer of an art."""
    
    def __init__(self, art, index: int= 0) -> None:

        super().__init__(art.width, art.height)
        self.art = art
        self.index = index
    
    def _load(self):
        need_to_unload = False
        if not self.art.is_loaded:
            need_to_unload = True
            self.art.load()
        
        self.matrix = 1 - sa.array_alpha(self.art.surfaces[self.index])/255

        if need_to_unload:
            self.art.unload()

class FromArtColor(Mask):
    """
    A mask from a mapping of the color layers.
    
    Every pixel of the art is mapped to a value betwenn 0 and 1.
    Selects only one image of the art based on the index.
    """

    def __init__(self, width: int, height: int, art, map: Callable[[int, int, int], float], index: int = 0) -> None:
        super().__init__(art.width, art.height)
        self.art = art
        self.index = index
        self.map = map

    def _load(self):
        need_to_unload = False
        if not self.art.is_loaded:
            need_to_unload = True
            self.art.load()
        
        self.matrix = np.apply_along_axis(self.map, 2, sa.array2d(self.art.surfaces[self.index]))

        if need_to_unload:
            self.art.unload()

class FromImageColor(Mask):
    """
    A mask from an image.
    
    Every pixel of the image is mapped to a value betwenn 0 and 1.
    """

    def __init__(self, width: int, height: int, path: str, map: Callable[[int, int, int], float]) -> None:
        self.path = get_file('images', path)
        self.im = Image.open(self.path)
        width, height = self.im.size
        super().__init__(width, height)
        self.map = map
    
    def _load(self):
        rgb_array = np.array(self.im.convert('RGB'))
        self.matrix = np.apply_along_axis(self.map, 2, rgb_array)

class FromImageColor(Mask):
    """
    A mask from the alpha layer of an image.
    """

    def __init__(self, width: int, height: int, path: str) -> None:
        self.path = get_file('images', path)
        self.im = Image.open(self.path)
        width, height = self.im.size
        super().__init__(width, height)
    
    def _load(self):
        try:
            rgba_array = np.array(self.im.convert('RGBA'))
        except:
            raise PygamingException(f"The image {self.path} do not have any alpha layer and thus cannot create a mask.")

        self.matrix = rgba_array[:, :, 3]

class _MaskCombination(Mask, ABC):
    """MaskCombinations are abstract class for all mask combinations: sum, products and average"""

    def __init__(self, *masks: Mask):

        if any(mask.width != masks[0].width or mask.height != masks[0].height for mask in masks):
            raise PygamingException("All masks must have the same shape.")
        super().__init__(masks[0].width, masks[0].height)
        self.masks = masks
    
    @abstractmethod
    def _combine(self, *matrices: np.ndarray) -> np.ndarray:
        raise NotImplementedError()

    def _load(self):
        for mask in self.masks:
            if not mask.is_loaded():
                mask.load()
        
        self._combine(*(mask.matrix for mask in self.masks))

class SumOfMasks(_MaskCombination):


    def _combine(self, *matrices):
        return np.clip(np.sum(matrices))

class ProductOfMasks(_MaskCombination):

    def _combine(self, *matrices):
        return np.prod(matrices)

class AverageOfMasks(_MaskCombination):

    def __init__(self, *masks: Mask, weights= None):
        if weights is None:
            weights = [1]*len(masks)
        super().__init__(*masks)
        self.weights = weights

    def _combine(self, *matrices):
        self.matrix = 0
        for matrix, weight in zip(matrices, self.weights):
            self.matrix += matrix*weight
        
        self.matrix /= sum(self.weights)
    
class BlitMaskOnMask(_MaskCombination):

    def __init__(self, background: Mask, foreground: Mask, threshold: float = 0, reverse: bool = False):
        super().__init__(background, foreground)
        self.threshold = threshold
        self.reverse = reverse

    def _combine(self, background_matrix, foreground_matrix) -> np.ndarray:
        self.matrix = background_matrix
        if not self.reverse:
            positions_to_keep = foreground_matrix > self.threshold
        else:
            positions_to_keep = foreground_matrix < self.threshold
        self.matrix[positions_to_keep] = foreground_matrix[positions_to_keep]

class InvertedMask(Mask):

    def __init__(self, mask: Mask):
        super().__init__(mask.width, mask.height)
        self._mask = mask
    
    def _load(self):
        if not self._mask.is_loaded():
            self._mask.load()
        self.matrix = 1 - self._mask.matrix