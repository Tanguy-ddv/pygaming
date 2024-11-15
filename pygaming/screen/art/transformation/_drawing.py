from pygame import Surface, draw, gfxdraw
from typing import Sequence
from ._transformation import Transformation
from ....color import ColorLike

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
