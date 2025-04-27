"""The actor module contain the actor."""
import math
from typing import Optional
from pygame import transform as tf
from .frame import Frame
from .anchors import AnchorLike, TOP_LEFT, Anchor
from .hover import Hoverable
from .art import Art
from .hitbox import Hitbox
from ..inputs.mouse import Click
from .hover import Tooltip, Cursor

class Actor(Hoverable):
    """
    An actor is an object that is made to move and possibly rotate in a frame.
    
    Methods to define:
    - start()
    - end()
    - update()
    """

    def __init__(
        self,
        master: Frame,
        main_art: Art,
        hitbox: Hitbox = None,
        tooltip: Tooltip = None,
        cursor: Cursor = None,
        update_if_invisible: bool = False,
        continue_animation: bool = False
    ) -> None:
        super().__init__(
            master=master,
            art=main_art,
            hitbox=hitbox,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible
        )
        self._angle = 0
        self._zoom = 1
        self._initial_size = self.width, self.height
        self._initial_anchor = None

    def place(self, x: int, y:int, anchor: AnchorLike = TOP_LEFT, angle: float = 0, zoom: float = 1, layer: int = 0):
        self._initial_anchor = Anchor(anchor)
        self._angle = angle
        self._zoom = zoom
        return super().place(x, y, anchor, layer)

    def translate(self, dx, dy):
        """Translate the actor in the frame by a given value."""
        if self._x is not None:
            self._x += dx
            self._y += dy

            self.on_master = self.get_on_master()
            if self.on_master:
                self.master.notify_change()

    def make_surface(self):
        """Create the current surface."""

        surface = self._arts.get(self.state, **self.game.settings)
        if self._angle or self._zoom != 1:
            surface = tf.rotozoom(surface, self._angle, self._zoom)
        return surface

    def is_contact(self, pos: Optional[Click | tuple[int, int]]):
        """Return True if the mouse is hovering the element."""
        if pos is None or (not self.on_master and isinstance(pos, Click)):
            return False
        if isinstance(pos, tuple):
            pos = Click(*pos)
        ck = pos.make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio)
        pos = ck.x, ck.y
        if self._zoom != 1:
            # modify the position to take the zoom into account.
            x,y = pos
            x/= self._zoom
            y/= self._zoom
            pos = x,y
        if self._angle:
            # modify the position to take the angle into account.
            x,y = pos # relative to the top left of the element this is the hitbox
            rel_x = x - self.width/2 # relative to the center of the element.
            rel_y = y - self.height/2

            rad = math.radians(self._angle)
            cos_a, sin_a = math.cos(rad), math.sin(rad)

            orig_x = cos_a * rel_x - sin_a * rel_y # relative to the center of the element, before rotation
            orig_y = sin_a * rel_x + cos_a * rel_y

            pos = orig_x + self._initial_size[0]/2, orig_y + self._initial_size[1]/2
        return self.hitbox.is_contact(pos)

    def _find_new_anchor(self):
        w, h = self.width, self.height # the size before any rotation

        theta = math.radians(-self._angle)
        self.width = int(w * abs(math.cos(theta)) + h * abs(math.sin(theta)))
        self.height = int(h * abs(math.cos(theta)) + w * abs(math.sin(theta)))

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
