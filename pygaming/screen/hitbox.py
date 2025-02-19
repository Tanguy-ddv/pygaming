"""This module contains the hitbox class."""

from pygame import Rect
from .art import mask
from gamarts._common import LoadingError

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

    def get_at(self, pos: tuple[int, int]):
        """Return whether the object having this hitbox is in contact with a point with the same relative position."""
        if self._mask is None:
            return self._rect.collidepoint(pos)
        elif not self._mask.is_loaded():
            return self._rect.collidepoint(pos) and self._mask.matrix[pos[0] - self._rect.left, pos[1] - self._rect.top] > 0
        else:
            raise LoadingError("The hitbox's mask isn't loaded.")

    def load(self, settings):
        if self._mask is not None:
            self._mask.load(*self.size, **settings)
