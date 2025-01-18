"""
The mask module contains masks. Masks are objects used to select part of an image on which apply an effect.
There are 5 types of Masks:
The first type is composed of only one class: MatrixMask
The second one is composed of binary geometrical masks: Circle, Ellipsis, Rectangle etc.
The third one is composed of gradient geometrical masks: GradientCircle, GradientRectangle etc.
The fourth one is composed of masks extracted from arts or from images.
The last one is combinations or transformation of other masks.
"""

from abc import ABC, abstractmethod
from typing import Callable
import numpy as np
from PIL import Image
import cv2
from pygame import Surface, surfarray as sa, SRCALPHA, draw, Rect
from ..error import PygamingException
from ..file import get_file
from ..settings import Settings

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
        pass

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

class FromArtAlpha(Mask):
    """A mask from the alpha layer of an art."""

    def __init__(self, art, index: int= 0) -> None:

        super().__init__(art.width, art.height)
        self.art = art
        self.index = index

    def _load(self, settings: Settings):
        need_to_unload = False
        if not self.art.is_loaded:
            need_to_unload = True
            self.art.load(settings)

        self.matrix = 1 - sa.array_alpha(self.art.surfaces[self.index])/255

        if need_to_unload:
            self.art.unload()

class FromArtColor(Mask):
    """
    A mask from a mapping of the color layers.
    
    Every pixel of the art is mapped to a value between 0 and 1 with the provided function.
    Selects only one image of the art based on the index.
    """

    def __init__(self, art, function: Callable[[int, int, int], float], index: int = 0) -> None:
        super().__init__(art.width, art.height)
        self.art = art
        self.index = index
        self.map = function

    def _load(self, settings: Settings):
        need_to_unload = False
        if not self.art.is_loaded:
            need_to_unload = True
            self.art.load(settings)

        self.matrix = np.apply_along_axis(self.map, 2, sa.array2d(self.art.surfaces[self.index]))

        if need_to_unload:
            self.art.unload()

class FromImageColor(Mask):
    """
    A mask from an image.
    
    Every pixel of the art is mapped to a value between 0 and 1 with the provided function.
    """

    def __init__(self, path: str, function: Callable[[int, int, int], float]) -> None:
        self.path = get_file('images', path)
        self.im = Image.open(self.path)
        width, height = self.im.size
        super().__init__(width, height)
        self.map = function

    def _load(self, settings: Settings):
        rgb_array = np.array(self.im.convert('RGB'))
        self.matrix = np.apply_along_axis(self.map, 2, rgb_array)

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

    def _load(self, settings: Settings):
        for mask in self.masks:
            if not mask.is_loaded():
                mask.load(settings)

        self._combine(*(mask.matrix for mask in self.masks))

class SumOfMasks(_MaskCombination):
    """
    A sum of mask is a mask based on the sum of the matrixes of the masks, clamped between 0 and 1.
    For binary masks, it acts like union.
    """

    def _combine(self, *matrices):
        return np.minimum(np.sum(matrices), 1)

class ProductOfMasks(_MaskCombination):
    """
    A product of mask is a mask based on the product of the matrixes of the masks.
    For binary masks, it acts like intersections.
    """

    def _combine(self, *matrices):
        return np.prod(matrices)

class AverageOfMasks(_MaskCombination):
    """
    An average of mask is a mask based on the average of the matrixes of the masks.
    """

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
    """
    A blit mask on mask is a mask where the values of the background below (or above) a given threshold are replaced
    by the values on the foreground.
    """

    def __init__(self, background: Mask, foreground: Mask, threshold: float = 0, reverse: bool = False):
        super().__init__(background, foreground)
        self.threshold = threshold
        self.reverse = reverse
    #pylint: disable=arguments-differ
    def _combine(self, background_matrix, foreground_matrix) -> np.ndarray:
        self.matrix = background_matrix
        if self.reverse:
            positions_to_keep = background_matrix < self.threshold
        else:
            positions_to_keep = background_matrix > self.threshold
        self.matrix[positions_to_keep] = foreground_matrix[positions_to_keep]

class InvertedMask(Mask):
    """
    An inverted mask is a mask whose value are the opposite of the parent mask.
    """

    def __init__(self, mask: Mask):
        super().__init__(mask.width, mask.height)
        self._mask = mask

    def _load(self, settings: Settings):
        if not self._mask.is_loaded():
            self._mask.load(settings)
        self.matrix = 1 - self._mask.matrix

class TransformedMask(Mask):
    """
    A Transformed mask is a mask whose matrix is the transformation of the matrix of another mask.
    The transformation must be a numpy vectorized function or a function matrix -> matrix.
    """

    def __init__(self, mask: Mask, transformation: Callable[[float], float] | Callable[[np.ndarray], np.ndarray]):
        super().__init__(mask.width, mask.height)
        self._mask = mask
        self.transformation = transformation

    def _load(self, settings: Settings):
        if not self._mask.is_loaded():
            self._mask.load(settings)

        self.matrix = np.clip(self.transformation(self._mask.matrix), 0, 1)
        if self.matrix.shape != self._mask.matrix.shape:
            raise PygamingException(f"Shape of the mask changed from {self._mask.matrix.shape} to {self.matrix.shape}")

class BinaryMask(Mask):
    """
    A binary mask is a mask where every values are 0 or 1. It is based on another mask.
    The matrix of this mask is that every component is 1 if the value on the parent mask
    is above a thresold and 0 otherwise. (this is reversed if reverse is set to True).
    """

    def __init__(self, mask: Mask, threshold: float, reverse: bool = False):
        super().__init__(mask.width, mask.height)
        self.threshold = threshold
        self._mask = mask
        self.reverse = reverse

    def _load(self, settings: Settings):
        if not self._mask.is_loaded():
            self._mask.load(settings)

        if self.reverse:
            positions_to_keep = self._mask.matrix < self.threshold
        else:
            positions_to_keep = self._mask.matrix > self.threshold

        self.matrix = np.zeros_like(self._mask.matrix)
        self.matrix[positions_to_keep] = 1

class FreeMask(Mask):
    """A FreeMask is a mask whose matrix can be freely and explicitly change during the game."""

    def __init__(self, width, height, initial_matrix):
        super().__init__(width, height)
        self.__initial_matrix = initial_matrix
    
    def _load(self, settings):
        self.matrix = self.__initial_matrix

    def update_matrix(self, new_matrix: np.ndarray):
        if self.matrix.shape == new_matrix.shape:
            self.matrix = new_matrix
        else:
            raise ValueError(f"The matrices have two different shapes: {self.matrix.shape}, {new_matrix.shape}")

class _MovingMask(Mask, ABC):
    """An abstract class for all the moving masks."""
    
    def __init__(self, width, height):
        super().__init__(width, height)
        self._velocity_x = 0
        self._velocity_y = 0
    
    def set_velocity(self, vel_x, vel_y):
        """Update the velocity of the moving mask in pixel/sec. They can be negative"""
        self._velocity_x = vel_x/1000
        self._velocity_y = vel_y/1000

    @abstractmethod
    def update(self, loop_duration):
        raise NotImplementedError()

class _WrappingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would wrap around the edges."""

    def __init__(self, width, height):
        super().__init__(self)
    
    def update(self, loop_duration):
        """Update the matrix by rearanging the rows and columns."""

        Nx = self._velocity_x*loop_duration
        Ny = self._velocity_y*loop_duration

        num_rows, num_cols = self.matrix.shape

        # Normalize to a valid range
        Nx = Nx % num_rows if Nx >= 0 else -(abs(Nx) % num_rows)
        Ny = Ny % num_cols if Ny >= 0 else -(abs(Ny) % num_cols)

        if Nx != 0:
            self.matrix = np.concatenate((self.matrix[Nx:], self.matrix[:Nx]), axis=0)
        if Ny != 0:
            self.matrix = np.concatenate((self.matrix[:, Ny:], self.matrix[:, :Ny]), axis=1)

class _BouncingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would bounce on the edges."""
    
    def __init__(self, width, height):
        super().__init__(width, height)

class _DisappearingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would disappear through on the edges."""

    def __init__(self, width, height):
        super().__init__(width, height)