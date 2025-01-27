from typing import Sequence
import math
import numpy as np
from pygame import Surface, gfxdraw, Rect
from pygamecv import rectangle, line, lines, polygon, circle, ellipse, pie, arc, rounded_rectangle
from ._transformation import Transformation
from ....color import ColorLike
from ....settings import Settings

class DrawCircle(Transformation):
    """Draw a circle on the art."""

    def __init__(
        self,
        color: ColorLike,
        radius: int,
        center: tuple[int, int],
        thickness: int = 0,
        angle: float = 0.,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()

        self.radius = radius
        self.color = color
        self.thickness = thickness
        self.center = center
        self.allow_antialias = allow_antialias
        self.angle = angle

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(circle(surface, self.center, self.radius, self.color, self.thickness, antialias) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawRectangle(Transformation):
    """Draw a rectangle on the art."""
    def __init__(
        self,
        color: ColorLike,
        center: tuple[int, int],
        width: int,
        height: int,
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()  
        self.color = color
        self.width = width
        self.height = height
        self.center = center
        self.thickness = thickness
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        rect = Rect(0, 0, self.width, self.height)
        rect.center = self.center
        surfaces = tuple(rectangle(surface, rect, self.color, self.thickness) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawRoundedRectantle(Transformation):
    """Draw a rectangle on the art, with rounded corners."""
    def __init__(
        self,
        color: ColorLike,
        center: tuple[int, int],
        width: int,
        height: int,
        top_left: int,
        top_right: int = None,
        bottom_right: int = None,
        bottom_left: int = None,
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()  
        self.color = color
        self.width = width
        self.height = height
        self.center = center
        self.thickness = thickness
        self.allow_antialias = allow_antialias
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_right = bottom_right
        self.bottom_left = bottom_left

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        rect = Rect(0, 0, self.width, self.height)
        rect.center = self.center
        surfaces = tuple(rounded_rectangle(surface, rect, self.color, self.thickness, antialias, self.top_left, self.top_right, self.bottom_left, self.bottom_right) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawEllipse(Transformation):
    """Draw an ellipse on the art."""

    def __init__(self, color:ColorLike, x_radius: int, y_radius: int, center: tuple[int, int], thickness: int = 0, angle: int=0, allow_antialias: bool = True):
        self.color = color
        self.x_radius = x_radius
        self.y_radius = y_radius
        self.center = center
        self.angle = angle
        self.thickness = thickness
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(ellipse(surface, self.center, self.x_radius, self.y_radius, self.color, self.thickness, antialias, self.angle) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawPolygon(Transformation):
    """Draw a polygon on the art."""

    def __init__(
        self,
        color: ColorLike,
        points: Sequence[tuple[int, int]],
        thickness: int = 0,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()

        self.color = color
        self.points = points
        self.thickness = thickness
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(polygon(surface, self.points, self.color, self.thickness, antialias) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawLine(Transformation):
    """Draw one line on the art."""

    def __init__(self, color: ColorLike, p1: tuple[int, int], p2: tuple[int, int], thickness: int = 1, allow_antialias: bool = True) -> None:
        self.color = color
        self.p1 = p1
        self.p2 = p2
        self.thickness = thickness
        self.allow_antialias = allow_antialias
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(line(surface, self.p1, self.p2, self.color, self.thickness, antialias) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawLines(Transformation):
    """Draw lines on the art."""

    def __init__(self, color: ColorLike, points: Sequence[tuple[int, int]], thickness: int = 1, closed: bool = False, allow_antialias: bool = True) -> None:
        self.color = color
        self.points = points
        self.thickness = thickness
        self.closed = closed
        self.allow_antialias = allow_antialias
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(lines(surface, self.points, self.color, self.thickness, antialias) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawArc(Transformation):
    """Draw an arc on the art."""

    def __init__(
        self,
        color: ColorLike,
        ellipsis_center: tuple[int, int],
        horizontal_radius: int,
        vertical_radius: int,
        from_angle: int,
        to_angle: int,
        angle: int = 0,
        thickness: int = 1,
        allow_antialias: bool = True
    ) -> None:
        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = horizontal_radius
        self.ry = vertical_radius
        self.from_angle = from_angle
        self.to_angle = to_angle
        self.angle = angle
        self.allow_antialias = allow_antialias

        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(arc(surface, self.ellipsis_center, self.rx, self.ry, self.color, self.thickness, antialias, self.angle, self.from_angle, self.to_angle) for surface in surfaces)

        return surfaces, durations, introduction, index, width, height

class DrawPie(Transformation):
    """Draw an arc on the art."""

    def __init__(
        self,
        color: ColorLike,
        ellipsis_center: tuple[int, int],
        horizontal_radius: int,
        vertical_radius: int,
        from_angle: int,
        to_angle: int,
        angle: int = 0,
        thickness: int = 1,
        allow_antialias: bool = True
    ) -> None:
        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = horizontal_radius
        self.ry = vertical_radius
        self.from_angle = from_angle
        self.to_angle = to_angle
        self.angle = angle
        self.allow_antialias = allow_antialias

        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        antialias = self.allow_antialias and settings.antialias
        surfaces = tuple(pie(surface, self.ellipsis_center, self.rx, self.ry, self.color, self.thickness, antialias, self.angle, self.from_angle, self.to_angle) for surface in surfaces)
        return surfaces, durations, introduction, index, width, height

class DrawBezier(Transformation):
    """Draw a bezier curb on the art."""

    def __init__(self, color: ColorLike, points: Sequence[tuple[int, int]], steps: int) -> None:
        self.color = color
        self.points = points
        self.steps = steps
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, settings: Settings):
        for surf in surfaces:
            gfxdraw.bezier(surf, self.points, self.steps, self.color)
        return surfaces, durations, introduction, index, width, height
