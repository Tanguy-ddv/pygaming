"""The transformations submodule contains all masks able to move."""

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
    
    def get_center(self):
        """Get the current center of the moving geometry inside the mask."""
        return self._center

    def set_velocity(self, vel_x, vel_y):
        """Update the velocity of the moving mask in pixel/sec. They can be negative"""
        self._velocity_x = vel_x/1000
        self._velocity_y = vel_y/1000

    def _get_move(self, loop_duration):
        return int(self._velocity_x*loop_duration), int(self._velocity_y*loop_duration)

    @abstractmethod
    def update(self, loop_duration):
        raise NotImplementedError()

class _WrappingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would wrap around the edges."""

    def __init__(self, width, height, center: tuple[int, int] = None):
        super().__init__(width, height, center)

    def set_center(self, new_x: int, new_y: int):
        """Reset the position of the center."""
        Nx = new_x - self._center[0]
        Ny = new_y - self._center[1]
        self._move_matrix(Nx, Ny)
        self._center = (new_x, new_y)

    def _move_matrix(self, Nx, Ny):
        # Normalize to a valid range
        Nx = Nx % self.width if Nx >= 0 else -(abs(Nx) % self.width)
        Ny = Ny % self.height if Ny >= 0 else -(abs(Ny) % self.height)

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
    """This Circle is able to move. When it reaches an end, it come back on the opposite side."""
    
    def __init__(self, width, height, radius: int, center = None):
        Circle.__init__(self, width, height, radius, center)
        _WrappingMovingMask.__init__(self, width, height, center)

class WrappingMovingRectangle(_WrappingMovingMask, Rectangle):
    """This Rectangle is able to move. When it reaches an end, it come back on the opposite side."""

    def __init__(self, width, height, left: int, top: int, right: int, bottom: int):
        Rectangle.__init__(self, width, height, left, top, right, bottom)
        center = (right + left)//2, (bottom + top)//2
        _WrappingMovingMask.__init__(self, width, height, center)

class _BouncingMovingMask(_MovingMask):
    """An abstract class for all moving masks that would bounce on the edges."""
    
    def __init__(self, width, height, inner_mask: Mask, center: tuple[int, int] = None):
        super().__init__(width, height, center)
        self._dx, self._dy = inner_mask.width//2, inner_mask.height//2
        self._inner_mask = inner_mask

    def make_matrix(self):
        """Create the matrix of the mask based on the inner mask and its position on the screen"""
        self.matrix = np.eye(self._width, self._height)
        inner_matrix = self._inner_mask.matrix

        left = self._center[0] - self._dx
        right = self._center[0] + self._dx
        top = self._center[1] - self._dy
        bottom = self._center[1] - self._dy

        start_x = max(0, left)
        end_x = min(self._width, right + 1)
        start_y = max(0, top)
        end_y = min(self._height, bottom + 1)

        inner_start_x = max(0, -left)
        inner_end_x = self._inner_mask.width - max(0, right + 1 - self._width)
        inner_start_y = max(0, -top)
        inner_end_y = self._inner_mask.height - max(0, bottom + 1 - self._height)

        self.matrix[start_y:end_y, start_x:end_x] = inner_matrix[inner_start_y:inner_end_y, inner_start_x:inner_end_x]

    def _load(self, settings):
        if not self._inner_mask.is_loaded():
            self._inner_mask.load()
        self.make_matrix()

    def update(self, loop_duration):
        """Update the mask."""
        Nx, Ny = self._get_move(loop_duration)
        center_x, center_y = self._center[0] + Nx, self._center[1] + Ny
        # Clip and bounce the position of the center
        if center_x - self._dx < 0 and self._velocity_x < 0:
            self._velocity_x *= -1
            center_x += 2*(self._dx - center_x)
        elif center_x + self._dx > self.width and self._velocity_x > 0:
            self._velocity_x *= -1
            center_x -= 2*(center_x + self._dx - self.width)
        
        if center_y - self._dy < 0 and self._velocity_y < 0:
            self._velocity_y *= -1
            center_y += 2*(self._dy - center_y)
        elif center_y + self._dy > self.height and self._velocity_y > 0:
            self._velocity_y *= -1
            center_y -= 2*(center_y + self._dy - self.height)
        
        self._center = (center_x, center_y)
        self.make_matrix()

class _DisappearingMovingMask(_BouncingMovingMask):
    """An abstract class for all moving masks that would disappear through on the edges."""

    def __init__(self, width, height, inner_mask: Mask, center: tuple[int, int] = None):
        super().__init__(width, height, inner_mask, center)
    
    def update(self, loop_duration):
        """Update the mask"""
        Nx, Ny = self._get_move(loop_duration)
        self._center = self._center[0] + Nx, self._center[1] + Ny   
        self.make_matrix()
