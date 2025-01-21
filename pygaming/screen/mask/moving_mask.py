"""The transformations submodule contains all masks able to move."""
from typing import Callable
from abc import ABC, abstractmethod
import numpy as np
from .mask import Mask, Circle, GradientCircle, Rectangle, RoundedRectangle, GradientRectangle, Ellipse


class _MovingMask(Mask, ABC):
    """An abstract class for all the moving masks."""

    def __init__(self, width, height, center: tuple[int, int] = None):
        Mask.__init__(self, width, height)
        ABC.__init__(self)
        self._velocity_x = 0
        self._velocity_y = 0
        if center is None:
            center = width//2, height//2
        self._center = center

    def set_center(self, new_x: int, new_y: int):
        """Reset the position of the center."""
        self._center = (new_x, new_y)
        return self

    def get_center(self):
        """Get the current center of the moving geometry inside the mask."""
        return self._center

    def set_velocity(self, vel_x, vel_y):
        """Update the velocity of the moving mask in pixel/sec. They can be negative"""
        self._velocity_x = vel_x/1000
        self._velocity_y = vel_y/1000
        return self

    def _get_move(self, loop_duration):
        return int(self._velocity_x*loop_duration), int(self._velocity_y*loop_duration)

    @abstractmethod
    def update(self, loop_duration):
        raise NotImplementedError()

class _WrappingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would wrap around the edges."""

    def set_center(self, new_x: int, new_y: int):
        """Reset the position of the center."""
        Nx = new_x - self._center[0]
        Ny = new_y - self._center[1]
        self._move_matrix(Nx, Ny)
        self._center = (new_x, new_y)
        return self

    def _move_matrix(self, Nx, Ny):
        # Normalize to a valid range
        Nx = int(Nx % self.width if Nx >= 0 else -(abs(Nx) % self.width))
        Ny = int(Ny % self.height if Ny >= 0 else -(abs(Ny) % self.height))

        if Ny != 0:
            self.matrix = np.concatenate((self.matrix[-Ny:], self.matrix[:-Ny]), axis=0)
        if Nx != 0:
            self.matrix = np.concatenate((self.matrix[:, -Nx:], self.matrix[:, :-Nx]), axis=1)

    def update(self, loop_duration):
        """Update the matrix by rearanging the rows and columns."""
        if self._velocity_x or self._velocity_y:
            Nx, Ny = self._get_move(loop_duration)
            self._move_matrix(Nx, Ny)
            self._center = (self._center[0] + Nx, self._center[1] + Ny)

class WrappingMovingCircle(_WrappingMovingMask, Circle):
    """This Circle is able to move. When it reaches an end, it comes back on the opposite side."""

    def __init__(self, width: int, height: int, radius: int, center: tuple[int, int] = None):
        Circle.__init__(self, width, height, radius, center)
        _WrappingMovingMask.__init__(self, width, height, self.center)

class WrappingMovingRectangle(_WrappingMovingMask, Rectangle):
    """This Rectangle is able to move. When it reaches an end, it comes back on the opposite side."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int):
        Rectangle.__init__(self, width, height, left, top, right, bottom)
        center = (right + left)//2, (bottom + top)//2
        _WrappingMovingMask.__init__(self, width, height, center)

class WrappingMovingEllipse(_WrappingMovingMask, Ellipse):
    """This Ellipse is able to move. When it reaches an end, it comes back on the opposite side."""
    def __init__(self, width: int, height: int, x_radius: int, y_radius: int, center: tuple[int, int] = None):
        Ellipse.__init__(self, width, height, x_radius, y_radius, center)
        _WrappingMovingMask.__init__(self, width, height, self.center)

class WrappingMovingRoundedRectangle(_WrappingMovingMask, RoundedRectangle):
    """This Moving Rectangle is able to move. When it reaches an end, it comes back on the opposite side."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int, radius: int):
        RoundedRectangle.__init__(self, width, height, left, top, right, bottom, radius)
        center = (right + left)//2, (bottom + top)//2
        super().__init__(width, height, center)

class WrappingMovingGradientCircle(_WrappingMovingMask, GradientCircle):
    """This Gradient Circle is able to move. When it reaches an end, it comes back on the opposite side."""

    def __init__(self, width, height, inner_radius: int, outer_radius: int, transition: Callable, center: tuple[int, int] = None):
        GradientCircle.__init__(self, width, height, inner_radius, outer_radius, transition, center)
        _WrappingMovingMask.__init__(self, width, height, self.center)

class WrappingMovingGradientRectangle(_WrappingMovingMask, GradientRectangle):
    """This Gradient Rectangle is able to move. When it reaches an end, it comes back on the opposite side."""

    def __init__(self, width: int, height: int, inner_left: int, inner_top: int, inner_right: int, inner_bottom: int,
            outer_left: int, outer_top: int, outer_right: int, outer_bottom: int, transition: Callable[[float], float] = lambda x:x):
        GradientRectangle.__init__(self, width, height, inner_left, inner_top, inner_right, inner_bottom,
            outer_left, outer_top, outer_right, outer_bottom, transition)
        center = (inner_right + inner_left)//2, (inner_bottom + inner_top)//2
        _WrappingMovingMask.__init__(self, width, height, center)

class _BouncingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would bounce on the edges."""

    def __init__(self, width, height, inner_mask: Mask, center: tuple[int, int] = None):
        super().__init__(width, height, center)
        self._dx, self._dy = inner_mask.width, inner_mask.height
        self._inner_mask = inner_mask

    def make_matrix(self):
        """Create the matrix of the mask based on the inner mask and its position on the screen"""
        self.matrix = np.ones((self._width, self._height))

        padded_matrix = np.pad(self.matrix, (self._dx, self._dy), mode='constant')
        center_x = self._center[0] + self._dx
        center_y = self._center[1] + self._dy
        padded_matrix[center_x - self._dx//2 : center_x + self._dx//2, center_y - self._dy//2 : center_y + self._dy//2] = self._inner_mask.matrix
        self.matrix = padded_matrix[self._dx:-self._dx, self._dy:-self._dy]

    def _load(self, settings):
        if not self._inner_mask.is_loaded():
            self._inner_mask.load(settings)
        self.make_matrix()

    def update(self, loop_duration):
        """Update the mask."""
        Nx, Ny = self._get_move(loop_duration)
        center_x, center_y = self._center[0] + Nx, self._center[1] + Ny
        # Clip and bounce the position of the center
        if center_x - self._dx//2 < 0 and self._velocity_x < 0:
            self._velocity_x *= -1
            center_x += 2*(self._dx//2 - center_x)
        elif center_x + self._dx//2 > self.width and self._velocity_x > 0:
            self._velocity_x *= -1
            center_x -= 2*(center_x + self._dx//2 - self.width)

        if center_y - self._dy//2 < 0 and self._velocity_y < 0:
            self._velocity_y *= -1
            center_y += 2*(self._dy//2 - center_y)
        elif center_y + self._dy//2 > self.height and self._velocity_y > 0:
            self._velocity_y *= -1
            center_y -= 2*(center_y + self._dy//2 - self.height)

        self._center = (center_x, center_y)
        self.make_matrix()

class BouncingMovingCircle(_BouncingMovingMask):
    """This Circle is able to move. When it reaches an end, it bounces."""

    def __init__(self, width: int, height: int, radius: int, center: tuple[int, int] = None):
        inner_mask = Circle(radius*2, radius*2, radius, (radius, radius))
        super().__init__(width, height, inner_mask, center)

class BouncingMovingRectangle(_BouncingMovingMask):
    """This Rectangle is able to move. When it reaches an end, it bounces."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int):
        inner_mask = Rectangle(right - left, bottom - top, 0, 0, right - left, bottom - top)
        center = (right + left)//2, (bottom + top)//2
        super().__init__(width, height, inner_mask, center)

class BouncingMovingEllipse(_BouncingMovingMask):
    """This Ellipse is able to move. When it reaches an end, it bounces."""
    def __init__(self, width: int, height: int, x_radius: int, y_radius: int, center: tuple[int, int] = None):
        inner_mask = Ellipse(x_radius*2, y_radius*2, x_radius, y_radius, (x_radius, y_radius))
        super().__init__( width, height, inner_mask, center)

class BouncingMovingRoundedRectangle(_BouncingMovingMask):
    """This Moving Rectangle is able to move. When it reaches an end, it bounces."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int, radius: int):
        inner_mask = RoundedRectangle(right - left, bottom - top, 0, 0, right - left, bottom - top, radius)
        center = (right + left)//2, (bottom + top)//2
        super().__init__(width, height, inner_mask, center)

class BouncingMovingGradientCircle(_BouncingMovingMask):
    """This Gradient Circle is able to move. When it reaches an end, it bounces."""

    def __init__(self, width, height, inner_radius: int, outer_radius: int, transition: Callable, center: tuple[int, int] = None):
        inner_mask = GradientCircle(outer_radius*2, outer_radius*2, inner_radius, outer_radius, transition, (outer_radius, outer_radius))
        super().__init__(width, height, inner_mask, center)

class BouncingMovingGradientRectangle(_BouncingMovingMask):
    """This Gradient Rectangle is able to move. When it reaches an end, it bounces."""

    def __init__(self, width: int, height: int, inner_left: int, inner_top: int, inner_right: int, inner_bottom: int,
            outer_left: int, outer_top: int, outer_right: int, outer_bottom: int, transition: Callable[[float], float] = lambda x:x):
        inner_mask = GradientRectangle(
            width=outer_right - outer_left,
            height=outer_bottom - outer_top,
            inner_left= inner_left - outer_left,
            inner_right= outer_right - inner_right,
            inner_top= inner_top - outer_top,
            inner_bottom= outer_bottom - inner_bottom,
            outer_left=0,
            outer_right=outer_right - outer_left,
            outer_top=0,
            outer_bottom=outer_bottom - outer_top,
            transition=transition
        )
        center = (inner_right + inner_left)//2, (inner_bottom + inner_top)//2
        super().__init__(width, height, inner_mask, center)

class _DisappearingMovingMask(_BouncingMovingMask):
    """An abstract class for all moving masks that would disappear through on the edges."""

    def update(self, loop_duration):
        """Update the mask"""
        Nx, Ny = self._get_move(loop_duration)
        self._center = self._center[0] + Nx, self._center[1] + Ny
        self.make_matrix()

class DisappearingMovingCircle(_DisappearingMovingMask):
    """This Circle is able to move. When it reaches an end, it disappears through."""

    def __init__(self, width: int, height: int, radius: int, center: tuple[int, int] = None):
        inner_mask = Circle(radius*2, radius*2, radius, (radius, radius))
        super().__init__(width, height, inner_mask, center)

class DisappearingMovingRectangle(_DisappearingMovingMask):
    """This Rectangle is able to move. When it reaches an end, it disappears through."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int):
        inner_mask = Rectangle(right - left, bottom - top, 0, 0, right - left, bottom - top)
        center = (right + left)//2, (bottom + top)//2
        super().__init__(width, height, inner_mask, center)

class DisappearingMovingEllipse(_DisappearingMovingMask):
    """This Ellipse is able to move. When it reaches an end, it disappears through."""
    def __init__(self, width: int, height: int, x_radius: int, y_radius: int, center: tuple[int, int] = None):
        inner_mask = Ellipse(x_radius*2, y_radius*2, x_radius, y_radius, (x_radius, y_radius))
        super().__init__( width, height, inner_mask, center)

class DisappearingMovingRoundedRectangle(_DisappearingMovingMask):
    """This Moving Rectangle is able to move. When it reaches an end, it disappears through."""

    def __init__(self, width: int, height: int, left: int, top: int, right: int, bottom: int, radius: int):
        inner_mask = RoundedRectangle(right - left, bottom - top, 0, 0, right - left, bottom - top, radius)
        center = (right + left)//2, (bottom + top)//2
        super().__init__(width, height, inner_mask, center)

class DisappearingMovingGradientCircle(_DisappearingMovingMask):
    """This Gradient Circle is able to move. When it reaches an end, it disappears through."""

    def __init__(self, width, height, inner_radius: int, outer_radius: int, transition: Callable, center: tuple[int, int] = None):
        inner_mask = GradientCircle(outer_radius*2, outer_radius*2, inner_radius, outer_radius, transition, (outer_radius, outer_radius))
        super().__init__(width, height, inner_mask, center)

class DisappearingMovingGradientRectangle(_DisappearingMovingMask):
    """This Gradient Rectangle is able to move. When it reaches an end, it disappears through."""

    def __init__(self, width: int, height: int, inner_left: int, inner_top: int, inner_right: int, inner_bottom: int,
            outer_left: int, outer_top: int, outer_right: int, outer_bottom: int, transition: Callable[[float], float] = lambda x:x):
        inner_mask = GradientRectangle(
            width=outer_right - outer_left,
            height=outer_bottom - outer_top,
            inner_left= inner_left - outer_left,
            inner_right= outer_right - inner_right,
            inner_top= inner_top - outer_top,
            inner_bottom= outer_bottom - inner_bottom,
            outer_left=0,
            outer_right=outer_right - outer_left,
            outer_top=0,
            outer_bottom=outer_bottom - outer_top,
            transition=transition
        )
        center = (inner_right + inner_left)//2, (inner_bottom + inner_top)//2
        super().__init__(width, height, inner_mask, center)
