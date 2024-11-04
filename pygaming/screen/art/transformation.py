"""The transformation module contains the base class Transformation and all the subclasses."""
from abc import ABC, abstractmethod
import pygame.transform as tf
from pygame import Surface
from pygame import Rect
from ...color import Color

class Transformation(ABC):

    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def apply(
        self,
        surfaces: tuple[Surface],
        durations: tuple[int],
        introduction: int,
        index: int
    ) -> tuple[tuple[Surface], tuple[int], int, int]:
        """Apply the transformation"""
        raise NotImplementedError()
    
class TransformationPipeline(Transformation):
    """A Transformation pipeline is a successive list of transformations."""

    def __init__(self, *transfos) -> None:
        super().__init__()
        self._transformations: tuple[Transformation] = transfos
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        for transfo in self._transformations:
            surfaces, durations, introduction, index = transfo.apply(surfaces, durations, introduction, index)

class Rotate(Transformation):
    """The rotate transformation will rotate the art by a given angle."""
    
    def __init__(self, angle: float) -> None:
        super().__init__()
        self.angle = angle

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        rotated_surfaces = (tf.rotate(surf, self.angle) for surf in surfaces)
        return rotated_surfaces, durations, introduction, index

class Zoom(Transformation):
    """
    The zoom transformation will zoom the art by a give scale.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a scale of 1.2 would modify the art
    to a size (120, 120). Calling this transformation with a scale of 0.6 would modify the art
    to a size (60, 60).
    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        if self.scale == 2:
            rescaled_surfaces = (tf.scale2x(surf) for surf in surfaces)
        else:
            rescaled_surfaces = (tf.scale_by(surf, self.scale) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index

class Resize(Transformation):
    """
    The resize transformation will resize the art to a new size. The image might end distorded.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a zie of (120, 60) would modify the art
    to a size (120, 60)
    """

    def __init__(self, size: tuple[int, int]) -> None:
        super().__init__()
        self.size = size
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        rescaled_surfaces = (tf.scale(surf, self.size) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index

class Crop(Transformation):
    """
    The crop transformation crop the art to a smaller art.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a rect (50, 50, 20, 30) will result
    in a surface with only the pixels from (50, 50) to (70, 80)
    """

    def __init__(self, rect: Rect) -> None:
        super().__init__()
        self.rect = rect

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        background = Surface(self.rect.size)
        cropped_surfaces = []
        for surf in surfaces:
            background.blit(surf, 0, self.rect)
            cropped_surfaces.append(background)
        return tuple(cropped_surfaces), durations, introduction, index
    
class Padding(Transformation):
    """
    The pad transformation add a solid color extension on every side of the art. If the pad is negative, act like a crop.
    """

    def __init__(self, color: Color, left: int = 0, right = 0, top = 0, bottom = 0) -> None:
        super().__init__()
        self.color = color
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        h, w = surfaces[0].get_size()
        background = Surface((h + self.left + self.right, w + self.left + self.right))
        padded_surfaces = []
        for surf in surfaces:
            background.blit(surf, (self.left, self.top))
            padded_surfaces.append(background)
        return tuple(padded_surfaces), durations, introduction, index

class SetAlpha(Transformation):
    """
    The setalpha transformation replace the alpha value of all the pixel by a new value.
    Pixels that are transparent from the begining will not change.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__()
        self.alpha = alpha

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        alpha_surfaces = (surf.set_alpha(self.alpha) for surf in surfaces)
        return alpha_surfaces, durations, introduction, index
    
class Flip(Transformation):
    """
    The flip transformation flips the art, horizontally and/or vertically.
    """

    def __init__(self, horizontal: bool, vertical: bool) -> None:
        super().__init__()
        self.horizontal = horizontal
        self.vertical = vertical

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        flipped_surfaces = (tf.flip(surf, self.horizontal, self.vertical) for surf in surfaces)
        return flipped_surfaces, durations, introduction, index

class VerticalChop(Transformation):
    """
    The vertical chop transformation remove a band of pixel and put the right side next to the left side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (from_, 0, to - from_, 0)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        chopped_surfaces = (tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, index

class HorizontalChop(Transformation):
    """
    The horizontal chop transformation remove a band of pixel and put the bottom side just below to the top side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (0, from_, 0, to - from_)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        chopped_surfaces = (tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, index

class GrayScale(Transformation):
    """
    The gray scale transformation turn the art into a black and white art.
    """

    def __init__(self) -> None:
        super().__init__()
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        graysurfeaces = (tf.grayscale(surf) for surf in surfaces)
        return graysurfeaces, durations, introduction, index

class SpeedUp(Transformation):
    """
    Speed up the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 50 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        new_durations = (d/self.scale for d in durations)
        return surfaces, new_durations, introduction, index

class SlowDown(Transformation):
    """
    Slow down the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 200 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        new_durations = (d*self.scale for d in durations)
        return surfaces, new_durations, introduction, index

class Extract(Transformation):
    """
    The extract transformation returns a subset of the images and durations of the art. Bounds are included
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        if self.from_ <= 0:
            raise ValueError(f"from argument cannot be negative, got {from_}")
        if self.from_ > self.to:
            raise ValueError(f'to argument must be superior to from_, got {to} and {from_}')
        self.from_ = from_
        self.to = to
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        this_to = len(surfaces) if self.to >= len(surfaces) else self.to

        if index >= this_to:
            index -= (self.from_ - this_to)
        elif index > self.from_:
            index = self.from_
        
        if introduction >= this_to:
            introduction -= (self.from_ - this_to)
        elif introduction > self.from_:
            introduction = self.from_
        return surfaces[self.from_ : this_to +1], durations[self.from_ : this_to + 1], introduction, index