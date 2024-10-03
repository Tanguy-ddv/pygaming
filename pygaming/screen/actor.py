"""The actor module contain the actor."""

from ..phase import GamePhase
from .element import Element, TOP_LEFT, SurfaceLike

class Actor(Element):
    """An actor is an object that is made to move and possibly rotate in a frame."""

    def __init__(
        self,
        master: GamePhase | Element,
        main_surface: SurfaceLike,
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
        self.main_surface.update_animation(loop_duration)

    def loop(self, loop_duration):
        """Update the frame at every loop."""
        self.update_animation(loop_duration)
        self.update(loop_duration)

    def translate(self, dx, dy):
        """Translate the actor in the frame by a given value."""
        self._x += dx
        self._y += dy

    def move(self, new_x, new_y):
        """Reset the position of the actor in the frame."""
        self._x = new_x
        self._y = new_y
