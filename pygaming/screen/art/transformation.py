"""The transformation module contains the base class Transformation and all the subclasses."""
from abc import ABC, abstractmethod
from math import cos, sin, radians
from typing import Sequence
import pygame.transform as tf
from pygame import Surface, SRCALPHA, Rect, draw, gfxdraw
from ...color import Color
from .colored_surfaces import ColorLike

class Transformation(ABC):

    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def apply(
        self,
        surfaces: tuple[Surface],
        durations: tuple[int],
        introduction: int,
        index: int,
        width: int,
        height: int
    ) -> tuple[tuple[Surface], tuple[int], int, int, int, int]:
        """Apply the transformation"""
        raise NotImplementedError()

    def get_new_dimension(self, width, height):
        """Calculate the new dimensions of the art after transformation."""
        return width, height
    
class Pipeline(Transformation):
    """A Transformation pipeline is a successive list of transformations."""

    def __init__(self, *transfos) -> None:
        super().__init__()
        self._transformations: tuple[Transformation] = transfos
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int) -> tuple[tuple[Surface], tuple[int], int, int, int, int]:
        for transfo in self._transformations:
            surfaces, durations, introduction, index, width, height = transfo.apply(surfaces, durations, introduction, index, width, height)
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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        rotated_surfaces = tuple(tf.rotate(surf, self.angle) for surf in surfaces)
        return rotated_surfaces, durations, introduction, index, *rotated_surfaces[0].get_size()

    def _get_rotated_dimensions(self, width, height, angle):
        """Calculate the new dimensions of the art after rotation."""
        radians_angle = radians(angle)

        new_width = abs(width * cos(radians_angle)) + abs(height * sin(radians_angle))
        new_height = abs(width * sin(radians_angle)) + abs(height * cos(radians_angle))
    
        return int(new_width), int(new_height)

    def get_new_dimension(self, width, height):
        return self._get_rotated_dimensions(width, height, self.angle)


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
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        if self.scale == 2:
            rescaled_surfaces = tuple(tf.scale2x(surf) for surf in surfaces)
        else:
            rescaled_surfaces = tuple(tf.scale_by(surf, self.scale) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index, int(width*self.scale), int(height*self.scale)

    def get_new_dimension(self, width, height):
        return int(width*self.scale), int(height*self.scale)

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
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
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

    def __init__(self, color: Color, left: int = 0, right = 0, top = 0, bottom = 0) -> None:
        super().__init__()
        self.color = color
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        background = Surface((width + self.left + self.right, height + self.left + self.right), SRCALPHA)
        background.fill(self.color)
        padded_surfaces = []
        for surf in surfaces:
            background.blit(surf, (self.left, self.top))
            padded_surfaces.append(background.copy())
        return tuple(padded_surfaces), durations, introduction, index, width + self.left + self.right, height + self.left + self.right

    def get_new_dimension(self, width, height):
        return width + self.left + self.right, height + self.left + self.right

class SetAlpha(Transformation):
    """
    The setalpha transformation replace the alpha value of all the pixel by a new value.
    Pixels that are transparent from the begining will not change.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__()
        self.alpha = alpha

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            surf.set_alpha(self.alpha)
        return surfaces, durations, introduction, index, width, height
    
class Flip(Transformation):
    """
    The flip transformation flips the art, horizontally and/or vertically.
    """

    def __init__(self, horizontal: bool, vertical: bool) -> None:
        super().__init__()
        self.horizontal = horizontal
        self.vertical = vertical

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        flipped_surfaces = tuple(tf.flip(surf, self.horizontal, self.vertical) for surf in surfaces)
        return flipped_surfaces, durations, introduction, index, height, width

    def get_new_dimension(self, width, height):
        return height, width

class VerticalChop(Transformation):
    """
    The vertical chop transformation remove a band of pixel and put the right side next to the left side.
    """

    def __init__(self, from_: int, to: int) -> None:
        super().__init__()
        self.rect = (from_, 0, to - from_, 0)

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        chopped_surfaces = tuple(tf.chop(surf, self.rect) for surf in surfaces)
        return chopped_surfaces, durations, introduction, index, width, height - self.rect[3]

    def get_new_dimension(self, width, height):
        return width, height - self.rect[3]

class GrayScale(Transformation):
    """
    The gray scale transformation turn the art into a black and white art.
    """

    def __init__(self) -> None:
        super().__init__()
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        graysurfeaces = tuple(tf.grayscale(surf) for surf in surfaces)
        return graysurfeaces, durations, introduction, index, width, height

class SpeedUp(Transformation):
    """
    Speed up the animation by a scale.

    Example.
    If the duration of each frame in the art is 100 ms and the scale is 2, each frame lasts now 50 ms.

    """

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        new_durations = tuple(d*self.scale for d in durations)
        return surfaces, new_durations, introduction, index, width, height

class ResetDurations(Transformation):
    """
    Reset the duration of every image in the art to a new value.
    """

    def __init__(self, new_duration: int) -> None:
        super().__init__()
        self.new_duration = new_duration

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        return surfaces, tuple(self.new_duration for _ in durations), introduction, index, width, height

class SetIntroductionIndex(Transformation):
    """
    Set the introduction to a new index.
    """
    def __init__(self, introduction: int) -> None:
        super().__init__()
        self.introduction = introduction
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        return surfaces, durations, self.introduction, index, width, height

class SetIntroductionTime(Transformation):
    """
    Set the introduction to a new index by specifying a time.
    """
    def __init__(self, introduction: int) -> None:
        super().__init__()
        self.introduction = introduction
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        
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
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
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

    def __init__(self) -> None:
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        return (surfaces[0],), (0,), 0, 0, width, height

class Last(Transformation):
    """Extract the very last frame of the animation."""

    def __init__(self) -> None:
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        return (surfaces[-1],), (0,), 0, 0, width, height

class ExtractOne(Transformation):
    """Extract the one frame of the animation."""

    def __init__(self, index: int) -> None:
        super().__init__()
        self.index = index

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        return (surfaces[self.index],), (0,), 0, 0, width, height

class DrawCircle(Transformation):
    """Draw a circle on the art."""

    def __init__(
        self,
        color: ColorLike,
        radius: int,
        center: tuple[int, int],
        thickness: int = 0,
        draw_top_right: bool = False,
        draw_top_left: bool = False,
        draw_bottom_left: bool = False,
        draw_bottom_right: bool = False,
    ) -> None:
        super().__init__()

        self.radius = radius
        self.color = color
        self.thickness = thickness
        self.draw_top_right = draw_top_right
        self.draw_top_left = draw_top_left
        self.draw_bottom_left = draw_bottom_left
        self.draw_bottom_right = draw_bottom_right
        self.center = center

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            draw.circle(surf, self.color, self.center, self.radius, self.thickness, self.draw_top_right, self.draw_top_left, self.draw_bottom_left, self.draw_bottom_right)
        return surfaces, durations, introduction, index, width, height

class DrawRectangle(Transformation):
    """Draw a rectangle on the art."""
    def __init__(
        self,
        color: ColorLike,
        left: int,
        top: int,
        width: int,
        height: int,
        thickness: int = 0,
        border_radius: int = 0,
        border_top_left_radius: int = -1,
        border_top_right_radius: int = -1,
        border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1,
    ) -> None:
        super().__init__()  
        self.color = color
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.thickness = thickness
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            draw.rect(
                surf,
                self.color,
                (self.left, self.top, self.width, self.height),
                self.thickness,
                self.border_radius,
                self.border_top_left_radius,
                self.border_top_right_radius,
                self.border_bottom_left_radius,
                self.border_bottom_right_radius)
        
        return surfaces, durations, introduction, index, width, height
    
class DrawPolygon(Transformation):
    """Draw a polygon on the art."""

    def __init__(
        self,
        color: ColorLike,
        points: Sequence[tuple[int, int]],
        thickness: int = 0) -> None:
        super().__init__()

        self.color = color
        self.points = points
        self.thickness = thickness

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            draw.polygon(surf, self.color, self.points, self.thickness)
        return surfaces, durations, introduction, index, width, height

class DrawLine(Transformation):
    """Draw one line on the art."""

    def __init__(self, color: ColorLike, p1: tuple[int, int], p2: tuple[int, int], thickness: int = 1) -> None:
        self.color = color
        self.p1 = p1
        self.p2 = p2
        self.thickness = thickness
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        if self.thickness == 1 and self.p1[0] == self.p2[0]:
            for surf in surfaces:
                gfxdraw.vline(surf, self.p1[0], self.p1[1], self.p2[1], self.color)
        elif self.thickness == 1 and self.p1[1] == self.p2[0]:
            for surf in surfaces:
                gfxdraw.hline(surf, self.p1[0], self.p2[0], self.p2[1], self.color)
        elif self.thickness == 1:
            for surf in surfaces:
                gfxdraw.line(surf, self.p1[0], self.p1[1], self.p2[0], self.p2[1], self.color)
        else:
            for surf in surfaces:
                draw.line(surf, self.color, (self.p1[0], self.p1[1]), (self.p2[0], self.p2[1]), self.thickness)
        return surfaces, durations, introduction, index, width, height

class DrawLines(Transformation):
    """Draw lines on the art."""

    def __init__(self, color: ColorLike, points: Sequence[tuple[int, int]], thickness: int = 1, closed: bool = False) -> None:
        self.color = color
        self.points = points
        self.thickness = thickness
        self.closed = closed
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            draw.lines(surf, self.color, self.closed, self.points, self.thickness)
        return surfaces, durations, introduction, index, width, height

class DrawArc(Transformation):
    """Draw an arc on the art."""

    def __init__(self, color: ColorLike, ellipsis_center: tuple[int, int], horizontal_radius: int, vertical_radius: int, from_angle: float, to_angle: float, thickness: int = 1) -> None:
        self.color = color
        self.rect = (ellipsis_center[0] - horizontal_radius, ellipsis_center[1] - vertical_radius, horizontal_radius*2, vertical_radius*2)
        self.thickness = thickness
        self.from_angle = from_angle
        self.to_angle = to_angle
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            draw.arc(surf, self.color, self.rect, self.from_angle, self.to_angle, self.thickness)
        return surfaces, durations, introduction, index, width, height

class DrawBezier(Transformation):
    """Draw a bezier curb on the art."""

    def __init__(self, color: ColorLike, points: Sequence[tuple[int, int]], steps: int) -> None:
        self.color = color
        self.points = points
        self.steps = steps
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int):
        for surf in surfaces:
            gfxdraw.bezier(surf, self.points, self.steps, self.color)
        return surfaces, durations, introduction, index, width, height
