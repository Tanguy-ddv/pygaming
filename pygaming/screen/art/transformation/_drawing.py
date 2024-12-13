from typing import Sequence
import math
import numpy as np
from pygame import Surface, draw, gfxdraw, SRCALPHA, transform, surfarray
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
        draw_top_right: bool = True,
        draw_top_left: bool = True,
        draw_bottom_left: bool = True,
        draw_bottom_right: bool = True,
        angle: float = 0.,
        allow_antialias: bool = True
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
        self.allow_antialias = allow_antialias
        self.angle = angle

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        antialias = antialias and self.allow_antialias
        background = Surface((self.radius*2, self.radius*2), SRCALPHA)
        if antialias:
            gfxdraw.aacircle(background, *self.center, self.radius, self.color)
        if self.thickness != 1:
            gfxdraw.filled_circle(background, *self.center, self.radius, self.color)
            if self.thickness > 1:
                gfxdraw.filled_circle(background, *self.center, self.radius - self.thickness, (0, 0, 0, 0))
                gfxdraw.aacircle(background, *self.center, self.radius - self.thickness, self.color)

        if not self.draw_top_left:
            background.fill((0, 0, 0, 0), (0, 0, self.radius, self.radius))
        if not self.draw_bottom_left:
            background.fill((0, 0, 0, 0), (0, self.radius, self.radius, self.radius))
        if not self.draw_top_right:
            background.fill((0, 0, 0, 0), (self.radius, 0, self.radius, self.radius))
        if not self.draw_bottom_right:
            background.fill((0, 0, 0, 0), (self.radius, self.radius, self.radius, self.radius))
        if self.angle != 0.:
            background = transform.rotate(background, self.angle)
        for surf in surfaces:
            surf.blit(background, (self.center[0] - self.radius, self.center[1] - self.radius))

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
        angle: int = 0,
        border_radius: int = 0,
        border_top_left_radius: int = -1,
        border_top_right_radius: int = -1,
        border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1,
        allow_antialias: bool = True
    ) -> None:
        super().__init__()  
        self.color = color
        self.width = width
        self.height = height
        self.center = center
        self.thickness = thickness
        self.angle = angle
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius
        self.allow_antialias = allow_antialias

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        rectangle_bg = Surface((self.width, self.height), SRCALPHA)
        if self.allow_antialias and antialias and (
            self.border_radius
            or self.border_top_left_radius != -1
            or self.border_top_right_radius != -1
            or self.border_bottom_left_radius !=-1
            or self.border_bottom_right_radius !=- 1
        ):
            radius = self.border_radius if self.border_top_left_radius == -1 else self.border_top_left_radius
            if radius:
                gfxdraw.aacircle(rectangle_bg, radius, radius, radius, self.color)

            radius = self.border_radius if self.border_top_right_radius == -1 else self.border_top_right_radius
            if radius:
                gfxdraw.aacircle(rectangle_bg, self.width - radius, radius, radius, self.color)

            radius = self.border_radius if self.border_bottom_left_radius == -1 else self.border_bottom_left_radius
            if radius:
                gfxdraw.aacircle(rectangle_bg, radius, self.height - radius, radius, self.color)

            radius = self.border_radius if self.border_bottom_right_radius == -1 else self.border_bottom_right_radius
            if radius:
                gfxdraw.aacircle(rectangle_bg, self.width - radius, self.height - radius, radius, self.color)

        draw.rect(
            rectangle_bg,
            self.color,
            rectangle_bg.get_rect(),
            self.thickness,
            self.border_radius,
            self.border_top_left_radius,
            self.border_top_right_radius,
            self.border_bottom_left_radius,
            self.border_bottom_right_radius
        )

        rectangle = transform.rotate(rectangle_bg, self.angle)
        rectangle_size = rectangle.get_size()
        for surf in surfaces:
            surf.blit(rectangle, (self.center[0] - rectangle_size[0]//2, self.center[1] - rectangle_size[1]//2))

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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        antialias = self.allow_antialias and antialias

        ellipse_bg = Surface((self.x_radius*2, self.y_radius*2), SRCALPHA)
        if antialias and self.thickness > 1:
            gfxdraw.aaellipse(ellipse_bg, self.x_radius, self.y_radius, self.x_radius, self.y_radius, self.color)
            gfxdraw.aaellipse(ellipse_bg, self.x_radius, self.y_radius, self.x_radius - self.thickness, self.y_radius - self.thickness, self.color)
            gfxdraw.ellipse(ellipse_bg, self.color, (0, 0, self.x_radius*2, self.y_radius*2), self.thickness)
        elif antialias and self.thickness == 1:
            gfxdraw.aaellipse(ellipse_bg, self.x_radius, self.y_radius, self.x_radius, self.y_radius, self.color)
        elif antialias and self.thickness == 0:
            gfxdraw.aaellipse(ellipse_bg, self.x_radius, self.y_radius, self.x_radius, self.y_radius, self.color)
            gfxdraw.ellipse(ellipse_bg, self.color, (0, 0, self.x_radius*2, self.y_radius*2), self.thickness)
        else:
            gfxdraw.ellipse(ellipse_bg, self.color, (0, 0, self.x_radius*2, self.y_radius*2), self.thickness)

        ellipse = transform.rotate(ellipse_bg, self.angle)
        ellipse_size = ellipse.get_size()
        for surf in surfaces:
            surf.blit(ellipse, (self.center[0] - ellipse_size[0]//2, self.center[1] - ellipse_size[1]//2))

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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        antialias = self.allow_antialias and antialias
        for surf in surfaces:
            if self.thickness < 2 and antialias:
                gfxdraw.aapolygon(surf, self.points, self.color)
            draw.polygon(surf, self.color, self.points, self.thickness)

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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        antialias = self.allow_antialias and antialias
        if self.thickness == 1 and self.p1[0] == self.p2[0] and not antialias:
            for surf in surfaces:
                gfxdraw.vline(surf, self.p1[0], self.p1[1], self.p2[1], self.color)
        elif self.thickness == 1 and self.p1[1] == self.p2[0] and not antialias:
            for surf in surfaces:
                gfxdraw.hline(surf, self.p1[0], self.p2[0], self.p2[1], self.color)
        elif self.thickness == 1 and not antialias:
            for surf in surfaces:
                gfxdraw.line(surf, self.p1[0], self.p1[1], self.p2[0], self.p2[1], self.color)
        elif self.thickness == 1 and antialias:
            for surf in surfaces:
                draw.aaline(surf, self.color, (self.p1[0], self.p1[1]), (self.p2[0], self.p2[1]))
        elif not antialias:
            for surf in surfaces:
                draw.line(surf, self.color, (self.p1[0], self.p1[1]), (self.p2[0], self.p2[1]), self.thickness)
        else: # The thickness is not one and there is antialias.

            d = (self.p2[0] - self.p1[0], self.p2[1] - self.p1[1])
            dis = math.hypot(*d)
            deltas = (-d[1]/dis*self.thickness/2, d[0]/dis*self.thickness/2)

            p1_1 = (self.p1[0] - deltas[0], self.p1[1] - deltas[1])
            p1_2 = (self.p1[0] + deltas[0], self.p1[1] + deltas[1])
            p2_1 = (self.p2[0] - deltas[0], self.p2[1] - deltas[1])
            p2_2 = (self.p2[0] + deltas[0], self.p2[1] + deltas[1])

            for surf in surfaces:

                gfxdraw.aapolygon(surf, (p1_1, p1_2, p2_2, p2_1), self.color)
                gfxdraw.filled_polygon(surf, (p1_1, p1_2, p2_2, p2_1), self.color)

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

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        antialias = self.allow_antialias and antialias

        if not antialias:
            for surf in surfaces:
                draw.lines(surf, self.color, self.closed, self.points, self.thickness)
        elif self.thickness == 1:
            for surf in surfaces:
                draw.aalines(surf, self.color, self.closed, self.points)
        else:
            if self.closed:
                points = list(*self.points, self.points[0])
            else:
                points = self.points
            previous_p2_1 = None
            previous_p2_2 = None
            for p1, p2 in zip(points[:-1], points[1:]):

                d = (p2[0] - p1[0], p2[1] - p1[1])
                dis = math.hypot(*d)
                deltas = (-d[1]/dis*self.thickness/2, d[0]/dis*self.thickness/2)

                p1_1 = (p1[0] - deltas[0], p1[1] - deltas[1])
                p1_2 = (p1[0] + deltas[0], p1[1] + deltas[1])
                p2_1 = (p2[0] - deltas[0], p2[1] - deltas[1])
                p2_2 = (p2[0] + deltas[0], p2[1] + deltas[1])

                for surf in surfaces:
                    gfxdraw.aapolygon(surf, (p1_1, p1_2, p2_2, p2_1), self.color)
                    gfxdraw.filled_polygon(surf, (p1_1, p1_2, p2_2, p2_1), self.color)
                    if previous_p2_1:
                        gfxdraw.aapolygon(surf, (previous_p2_1, previous_p2_2, p2_2, p2_1), self.color)
                        gfxdraw.filled_polygon(surf, (previous_p2_1, previous_p2_2, p2_2, p2_1), self.color)

        return surfaces, durations, introduction, index, width, height

class DrawArc(Transformation):
    """Draw an arc on the art."""

    def __init__(
        self,
        color: ColorLike,
        ellipsis_center: tuple[int, int],
        horizontal_radius: int,
        vertical_radius: int,
        from_angle: float,
        to_angle: float,
        thickness: int = 1,
        allow_antialias: bool = True
    ) -> None:
        self.color = color
        self.thickness = thickness
        self.ellipsis_center = ellipsis_center
        self.rx = horizontal_radius
        self.ry = horizontal_radius

        self.from_angle = from_angle*math.pi/180
        self.to_angle = to_angle*math.pi/180
        self.allow_antialias = allow_antialias


        dx, dy = np.ogrid[:horizontal_radius*2, :vertical_radius*2]
        dx = dx - horizontal_radius
        dy = dy - vertical_radius
        angles = np.atan2(dy, dx)

        self._pie_matrix = np.zeros((horizontal_radius*2, vertical_radius*2))
        if from_angle < to_angle:
            mask = (from_angle < angles) & (angles < to_angle)
        else:
            mask = (from_angle > angles) & (angles > to_angle)
        self._pie_matrix[mask] = 1

        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        antialias = self.allow_antialias and antialias
        background = Surface((self.rx*2, self.ry*2), SRCALPHA)
        if antialias and self.thickness != 1:
            gfxdraw.aaellipse(background, self.rx, self.ry, self.rx, self.ry, self.color)
            gfxdraw.aaellipse(background, self.rx, self.ry, self.rx - self.thickness, self.ry - self.thickness, self.color)
            gfxdraw.ellipse(background, self.color, (0, 0, self.rx*2, self.ry*2), self.thickness)
        elif antialias and self.thickness == 1:
            gfxdraw.aaellipse(background, self.rx, self.ry, self.rx, self.ry, self.color)
        else:
            gfxdraw.ellipse(background, self.color, (0, 0, self.rx*2, self.ry*2), self.thickness)

        alpha = surfarray.array_alpha(background)
        alpha *= self._pie_matrix

        for surf in surfaces:
            surf.blit(background, (self.ellipsis_center[0] - self.rx, self.ellipsis_center[1] - self.ry))
        return surfaces, durations, introduction, index, width, height

class DrawBezier(Transformation):
    """Draw a bezier curb on the art."""

    def __init__(self, color: ColorLike, points: Sequence[tuple[int, int]], steps: int) -> None:
        self.color = color
        self.points = points
        self.steps = steps
        super().__init__()

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            gfxdraw.bezier(surf, self.points, self.steps, self.color)
        return surfaces, durations, introduction, index, width, height
