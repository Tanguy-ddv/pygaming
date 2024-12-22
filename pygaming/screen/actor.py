"""The actor module contain the actor."""
import math
from ..phase import GamePhase
from .element import Element, TOP_LEFT
from .art.art import Art
from .art.transformation._transformation import Rotate

class Actor(Element):
    """An actor is an object that is made to move and possibly rotate in a frame."""

    def __init__(
        self,
        master: GamePhase | Element,
        main_surface: Art,
        x: int,
        y: int,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        layer: int = 0
    ) -> None:
        super().__init__(
            master,
            main_surface,
            x,
            y,
            anchor,
            layer,
            None,
            None,
            False,
            False
        )

        self.surfaces = [self.surface]

    @property
    def main_surface(self):
        """Alias for the surface. Represent the main surface of the object."""
        return self.surface

    def update_animation(self, loop_duration):
        """Update the animation of the main surface. Override this method if you have more surfaces."""
        self.main_surface.update(loop_duration)

    def loop(self, loop_duration):
        """Update the frame at every loop."""
        self.update_animation(loop_duration)
        self.update(loop_duration)

    def translate(self, dx, dy):
        """Translate the actor in the frame by a given value."""
        self._x += dx
        self._y += dy
        self.notify_change()

    def rotate(self, angle):
        """Rotate the actor."""
        w, h = self.main_surface.width, self.main_surface.height
        # rotate all frames
        for surface in self.surfaces:
            surface.transform(Rotate(angle))
        # determine the new anchor
        new_w, new_h = self.main_surface.width, self.main_surface.height
        center_x, center_y = w / 2, h / 2
        point = self._x*self.surface.width, self._y*self.surface.height
        rel_x, rel_y = point[0] - center_x, point[1] - center_y
        rad_angle = math.radians(-angle)
        new_rel_x = rel_x * math.cos(rad_angle) - rel_y * math.sin(rad_angle)
        new_rel_y = rel_x * math.sin(rad_angle) + rel_y * math.cos(rad_angle)
        self.anchor = (new_rel_x + new_w / 2)/new_w, (new_rel_y + new_h / 2)/new_h
        # notify the master for a change
        self.notify_change()
