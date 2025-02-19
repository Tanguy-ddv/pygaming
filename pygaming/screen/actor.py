"""The actor module contain the actor."""
import math
from typing import Optional
from pygame import transform as tf
from ..phase import GamePhase
from .element import Element, TOP_LEFT
from .art import Art
from .hitbox import Hitbox
from ..inputs.mouse import Click

class Actor(Element):
    """
    An actor is an object that is made to move and possibly rotate in a frame.
    
    Methods to define:
    - start()
    - end()
    - update()
    """

    def __init__(
        self,
        master: GamePhase | Element,
        main_art: Art,
        x: int,
        y: int,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        layer: int = 0,
        hitbox: Hitbox = None,
        update_if_invisible: bool = False
    ) -> None:
        super().__init__(
            master,
            main_art,
            x,
            y,
            anchor,
            layer,
            None,
            None,
            False,
            False,
            hitbox,
            update_if_invisible=update_if_invisible
        )

        self._arts = {"main" : self.background}
        self._current_art = "main"
        self._angle = 0
        self._zoom = 1
        self._initial_anchor = anchor

    @property
    def main_art(self):
        """Alias for the main art. Represent the main art of the object."""
        return self.background

    def update_animation(self, loop_duration):
        """Update the animation of the main surface."""
        self._arts[self._current_art].update(loop_duration)

    def loop(self, loop_duration):
        """Update the frame at every loop."""
        self.update_animation(loop_duration)
        self.update(loop_duration)

    def translate(self, dx, dy):
        """Translate the actor in the frame by a given value."""
        self._x += dx
        self._y += dy

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()
    
    def make_surface(self):
        """Create the current surface."""
        surface = self._arts[self._current_art].get(None, **self.game.settings, copy=False)
        if self._angle or self._zoom != 1:
            surface = tf.rotozoom(surface, self._angle, self._zoom)
        return surface

    def is_contact(self, pos: Optional[Click | tuple[int, int]]):
        """Return True if the mouse is hovering the element."""
        if pos is None or (not self.on_master and isinstance(pos, Click)):
            return False
        if isinstance(pos, tuple):
            click = Click(*pos)
        ck = click.make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio)
        return self._active_area.is_contact((ck.x, ck.y), (self.width, self.height), self._angle, self._zoom)

    def _find_new_anchor(self):
        w, h = self.main_art.width, self.main_art.height # the size before any rotation

        theta = math.radians(self._angle)
        self.width, self.height = int(w * abs(math.cos(theta)) + h * abs(math.sin(theta))), int(h * abs(math.cos(theta)) + w * abs(math.sin(theta)))

        point = self._initial_anchor[0]*w, self._initial_anchor[1]*h # the point of anchor before rotation
        rel_x, rel_y = point[0] - w / 2, point[1] - h / 2 # relative to the old center
        new_rel_x = (rel_x * math.cos(theta) - rel_y * math.sin(theta)) # relative to the new center
        new_rel_y = (rel_x * math.sin(theta) + rel_y * math.cos(theta))
        self.anchor = (new_rel_x + self.width / 2)/self.width, (new_rel_y + self.height / 2)/self.height

    def rotate(self, angle):
        """Rotate the actor."""
        self._angle += angle
        self._find_new_anchor()
        self.get_on_master()
        self.notify_change()

    def zoom(self, zoom):
        """Zoom the actor."""
        self._zoom *= zoom
        self.width *= zoom
        self.height *= zoom
        self.get_on_master()
        self.notify_change()
