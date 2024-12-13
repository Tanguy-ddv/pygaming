"""The transformation module contains the base class Transformation and all the subclasses."""
from abc import ABC, abstractmethod
from math import cos, sin, radians
import pygame.transform as tf
from pygame import Surface, SRCALPHA, Rect
from ....color import ColorLike

class Transformation(ABC):
    """A transformation is an operation on an art."""

    @abstractmethod
    def apply(
        self,
        surfaces: tuple[Surface],
        durations: tuple[int],
        introduction: int,
        index: int,
        width: int,
        height: int,
        antialias: bool
    ):
        """Apply the transformation"""
        raise NotImplementedError()

    def get_new_dimension(self, width, height):
        """Calculate the new dimensions of the art after transformation."""
        return width, height

class Pipeline(Transformation):
    """A Transformation pipeline is a list of successive transformations."""

    def __init__(self, *transfos) -> None:
        super().__init__()
        self._transformations: tuple[Transformation] = transfos

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for transfo in self._transformations:
            surfaces, durations, introduction, index, width, height = transfo.apply(surfaces, durations, introduction, index, width, height, antialias)
        return surfaces, durations, introduction, index, width, height

    def get_new_dimension(self, width, height):
        for transfo in self._transformations:
            width, height = transfo.get_new_dimension(width, height)
        return width, height

class Rotate(Transformation):
    """The rotate transformation will rotate the art by a given angle."""

    def __init__(self, angle: float) -> None:
        super().__init__()
        self.angle = angle

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        rotated_surfaces = tuple(tf.rotate(surf, self.angle) for surf in surfaces)
        return rotated_surfaces, durations, introduction, index, *rotated_surfaces[0].get_size()

    def get_new_dimension(self, width, height):
        radians_angle = radians(self.angle)
        new_width = abs(width * cos(radians_angle)) + abs(height * sin(radians_angle))
        new_height = abs(width * sin(radians_angle)) + abs(height * cos(radians_angle))
        return int(new_width), int(new_height)


class Zoom(Transformation):
    """
    The zoom transformation will zoom the art by a give scale.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a scale of 1.2 would modify the art
    to a size (120, 120). Calling this transformation with a scale of 0.6 would modify the art
    to a size (60, 60). You can also specify two scales (one for horizontal and one for vertical) by passing
    a tuple as scale. If smooth is True, use a smooth zooming instead.
    """

    def __init__(self, scale: float | tuple[float, float], smooth: bool = False) -> None:
        super().__init__()
        self.scale = scale
        self.smooth = smooth

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        if (self.scale == (2, 2) or self.scale == 2) and not self.smooth:
            rescaled_surfaces = tuple(tf.scale2x(surf) for surf in surfaces)
        elif not self.smooth:
            rescaled_surfaces = tuple(tf.scale_by(surf, self.scale) for surf in surfaces)
        else:
            rescaled_surfaces = tuple(tf.smoothscale_by(surf, self.scale) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index, int(width*self.scale), int(height*self.scale)

    def get_new_dimension(self, width, height):
        return int(width*self.scale), int(height*self.scale)

class Resize(Transformation):
    """
    The resize transformation will resize the art to a new size. The image might end distorded.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with a zie of (120, 60) would modify the art
    to a size (120, 60). If smooth is True, use a smooth resizing instead.
    """

    def __init__(self, size: tuple[int, int], smooth: bool = False) -> None:
        super().__init__()
        self.size = size
        self.smooth = smooth

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        if self.smooth:
            rescaled_surfaces = tuple(tf.smoothscale(surf, self.size) for surf in surfaces)
        else:
            rescaled_surfaces = tuple(tf.scale(surf, self.size) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index, *self.size

    def get_new_dimension(self, width, height):
        return self.size

class Crop(Transformation):
    """
    The crop transformation crop the art to a smaller art.

    Example:
    ----
    If the art have a size of (100, 100), calling this transformation with left=50, top=50, width=20, height=30 will result
    in a surface with only the pixels from (50, 50) to (70, 80)
    """

    def __init__(self, left: int, top: int, width: int, height: int) -> None:
        super().__init__()
        self.rect = Rect(left, top, width, height)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        background = Surface(self.rect.size)
        cropped_surfaces = []
        for surf in surfaces:
            background.blit(surf, (0,0), self.rect)
            cropped_surfaces.append(background.copy())
        return tuple(cropped_surfaces), durations, introduction, index, *self.rect.size

    def get_new_dimension(self, width, height):
        return self.rect.size

class Padding(Transformation):
    """
    The pad transformation add a solid color extension on every side of the art. If the pad is negative, act like a crop.
    """

    def __init__(self, color: ColorLike, left: int = 0, right = 0, top = 0, bottom = 0) -> None:
        super().__init__()
        self.color = color
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        background = Surface((width + self.left + self.right, height + self.left + self.right), SRCALPHA)
        background.fill(self.color)
        padded_surfaces = []
        for surf in surfaces:
            background.blit(surf, (self.left, self.top))
            padded_surfaces.append(background.copy())
        return tuple(padded_surfaces), durations, introduction, index, width + self.left + self.right, height + self.left + self.right

    def get_new_dimension(self, width, height):
        return width + self.left + self.right, height + self.left + self.right

class Flip(Transformation):
    """
    The flip transformation flips the art, horizontally and/or vertically.
    """

    def __init__(self, horizontal: bool, vertical: bool) -> None:
        super().__init__()
        self.horizontal = horizontal
        self.vertical = vertical

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        flipped_surfaces = tuple(tf.flip(surf, self.horizontal, self.vertical) for surf in surfaces)
        return flipped_surfaces, durations, introduction, index, height, width

    def get_new_dimension(self, width, height):
        return width, height

class Transpose(Transformation):
    """The transpose transformation transpose the art like a matrix."""

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        tp_surfaces = tuple(tf.flip(tf.rotate(surf, 270), True, False) for surf in surfaces)
        return tp_surfaces, durations, introduction, index, width, height

    def get_new_dimension(self, width, height):
        return height, width

class VerticalChop(Transformation):
    """
    The vertical chop transformation remove a band of pixel and put the right side next to the left side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (from_, 0, to - from_, 0)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        chopped_surfaces = tuple(tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, index, width - self.rect[2], height

    def get_new_dimension(self, width, height):
        return width - self.rect[2], height

class HorizontalChop(Transformation):
    """
    The horizontal chop transformation remove a band of pixel and put the bottom side just below to the top side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (0, from_, 0, to - from_)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        chopped_surfaces = tuple(tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, index, width, height - self.rect[3]

    def get_new_dimension(self, width, height):
        return width, height - self.rect[3]

class SpeedUp(Transformation):
    """
    Speed up the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 50 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        new_durations = tuple(d/self.scale for d in durations)
        return surfaces, new_durations, introduction, index, width, height

class SlowDown(Transformation):
    """
    Slow down the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 200 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        new_durations = tuple(d*self.scale for d in durations)
        return surfaces, new_durations, introduction, index, width, height

class ResetDurations(Transformation):
    """
    Reset the duration of every image in the art to a new value.
    """

    def __init__(self, new_duration: int) -> None:
        super().__init__()
        self.new_duration = new_duration

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        return surfaces, tuple(self.new_duration for _ in durations), introduction, index, width, height

class SetIntroductionIndex(Transformation):
    """
    Set the introduction to a new index.
    """
    def __init__(self, introduction: int) -> None:
        super().__init__()
        self.introduction = introduction

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        return surfaces, durations, self.introduction, index, width, height

class SetIntroductionTime(Transformation):
    """
    Set the introduction to a new index by specifying a time.
    """
    def __init__(self, introduction: int) -> None:
        super().__init__()
        self.introduction = introduction

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):

        sum_dur = 0
        new_intro_idx = 0
        while sum_dur < self.introduction and new_intro_idx < len(durations):
            sum_dur += durations[new_intro_idx]
            new_intro_idx += 1

        return surfaces, durations, new_intro_idx, index, width, height

class ExtractMany(Transformation):
    """
    This transformation returns a subset of the images and durations of the art. Bounds are included
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        if from_ <= 0:
            raise ValueError(f"from argument cannot be negative, got {from_}")
        if from_ > to:
            raise ValueError(f'to argument must be superior to from_, got {to} < {from_}')
        self.from_ = from_
        self.to = to

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        this_to = len(surfaces) if self.to >= len(surfaces) else self.to

        if index >= this_to:
            index -= (self.from_ - this_to)
        elif index > self.from_:
            index = self.from_

        if introduction >= this_to:
            introduction -= (self.from_ - this_to)
        elif introduction > self.from_:
            introduction = self.from_
        return surfaces[self.from_ : this_to +1], durations[self.from_ : this_to + 1], introduction, index, width, height

class First(Transformation):
    """Extract the very first frame of the animation."""

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        return (surfaces[0],), (0,), 0, 0, width, height

class Last(Transformation):
    """Extract the very last frame of the animation."""

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        return (surfaces[-1],), (0,), 0, 0, width, height

class ExtractOne(Transformation):
    """Extract the one frame of the animation."""

    def __init__(self, index: int) -> None:
        super().__init__()
        self.index = index

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        return (surfaces[self.index],), (0,), 0, 0, width, height
