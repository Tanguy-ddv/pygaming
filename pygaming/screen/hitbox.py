"""This module contains the hitbox class."""
import math
from pygame import Rect
from .art import mask
from gamarts._common import LoadingError
from ..settings import Settings
from ..error import PygamingException

def __recover_original_size(new_width: int, new_height: int, sin_a: float, cos_a: float):
    cos_a, sin_a = abs(cos_a), abs(sin_a)
    
    th1 = (new_width + new_height) / 2 / (cos_a + sin_a)
    th2 = (new_width - new_height) / 2 / (cos_a - sin_a)
   
    w = th1 - th2
    h = th1 + th2

    return int(round(w)), int(round(h))

class Hitbox:
    """
    A Hitbox represent the pixel of contact. They can be a simple rectangle or have a mask.
    """

    def __init__(self, left: int, top: int, width: int, height: int, mask: mask.Mask = None):
        """
        Create a Hitbox.
        
        Params:
        ---
        - left, top, width, height: int, the rectangle representing the hitbox, relative to the object's whose hitbox is this.
        - mask: mask.Mask, if provided, a mask can be used to define more precisely the hitbox.
        """
        self._rect = Rect(left, top, width, height)
        self._mask = mask
        self._minimal_rect = self._rect
        self._initial_size = None
    
    def set_initial_size(self, size):
        """Set the initial size of the element this hitbox is refering to."""
        self._initial_size = size

    def is_contact(self, pos: tuple[int, int], element_size: tuple[int, int], angle: float = 0, zoom: float = 1):
        if zoom != 1:
            # modify the position to take the zoom into account.
            x,y = pos
            x/= zoom
            y/= zoom
            pos = x,y
        if angle:
            # modify the position to take the angle into account.
            x,y = pos # relative to the top left of the element this is the hitbox
            width, height = element_size
            rel_x = x - width/2 # relative to the center of the element.
            rel_y = y - height/2

            rad = math.radians(angle)
            cos_a, sin_a = math.cos(rad), math.sin(rad)

            orig_x = cos_a * rel_x - sin_a * rel_y # relative to the center of the element, before rotation
            orig_y = sin_a * rel_x + cos_a * rel_y

            pos = orig_x + self._initial_size[0]/2, orig_y + self._initial_size[1]/2
        return self.get_at(pos)

    def get_at(self, pos: tuple[int, int]):
        """Return whether the object having this hitbox is in contact with a point with the same relative position."""
        if self._mask is None:
            return self._rect.collidepoint(pos)
        elif self._mask.is_loaded():
            return self._rect.collidepoint(pos) and self._mask.matrix[pos[0] - self._rect.left, pos[1] - self._rect.top] > 0
        else:
            raise LoadingError("The hitbox's mask isn't loaded.")

    def load(self, settings: Settings):
        """Load the hitbox."""
        if self._mask is not None:
            self._mask.load(*self._rect.size, **settings)
            not_null_columns = self._mask.not_null_columns()
            not_null_rows = self._mask.not_null_rows()
            if not len(not_null_columns):
                raise PygamingException("The mask of this hitbox is empty.")
            self._minimal_rect = Rect(
                self._rect.left + not_null_columns[0],
                self._rect.top + not_null_rows[0],
                not_null_columns[-1] - not_null_columns[0],
                not_null_rows[-1] - not_null_rows[9]
            )

    def unload(self):
        """Unload the mask of the hitbox."""
        if self._mask is not None:
            self._mask.unload()
    
    def get_rect(self):
        """Get the rect of the hitbox."""
        return self._rect
    
    def get_mask(self):
        """Get the mask of the hitbox."""
        return self._mask

    @property
    def left(self):
        return self._minimal_rect.left
    
    @property
    def right(self):
        return self._minimal_rect.right
    
    @property
    def top(self):
        return self._minimal_rect.top
    
    @property
    def bottom(self):
        return self._minimal_rect.bottom