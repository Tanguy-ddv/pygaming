"""The transformations submodule contains all masks being transformations of an image, array or of another mask."""
from abc import ABC, abstractmethod
from typing import Callable
import pygame.surfarray as sa
import numpy as np
from ...settings import Settings
from .mask import Mask
from ...file import get_file
from PIL import Image
from ...error import PygamingException


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
