"""This module contains the hitbox class."""
from pygame import Rect
from gamarts._common import LoadingError
from .art import mask as mask_
from ..settings import Settings
from ..error import PygamingException
class _BooleanMask(mask_.Mask):
    """
    Boolean masks are masks with a matrix of bools.
    """

    def __init__(self, other: mask_.Mask):
        super().__init__()
        self.other = other

    def _load(self, width, height, **ld_kwargs):
        need_to_unload = False
        if not self.other.is_loaded():
            self.other.load(width, height, **ld_kwargs)
            need_to_unload = True
        self.matrix = self.other.matrix.astype(bool)
        if need_to_unload:
            self.other.unload()
class Hitbox:
    """
    A Hitbox represent the pixel of contact. They can be a simple rectangle or have a mask.
    """

    def __init__(self, left: int, top: int, width: int, height: int, mask: mask_.Mask = None):
        """
        Create a Hitbox.
        
        Params:
        ---
        - left, top, width, height: int, the rectangle representing the hitbox, relative to the object's whose hitbox is this.
        - mask: mask.Mask, if provided, a mask can be used to define more precisely the hitbox.
        """
        self._rect = Rect(left, top, width, height)
        self._mask = _BooleanMask(mask) if mask is not None else None
        self._minimal_rect = self._rect

    def is_contact(self, pos: tuple[int, int]):
        """Return whether the object having this hitbox is in contact with a point with the same relative position."""
        if self._mask is None:
            return self._rect.collidepoint(pos)
        elif self._mask.is_loaded():
            return self._rect.collidepoint(pos) and self._mask.matrix[pos[0] - self._rect.left, pos[1] - self._rect.top]
        else:
            raise LoadingError("The hitbox's mask isn't loaded.")

    def load(self, settings: Settings):
        """Load the hitbox."""
        if self._mask is not None and not self._mask.is_loaded():
            self._mask.load(*self._rect.size, **settings)
            not_null_columns = self._mask.not_null_columns()
            not_null_rows = self._mask.not_null_rows()
            if not not_null_columns.shape[0]:
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
        """The leftest column of the hitbox."""
        return self._minimal_rect.left

    @property
    def right(self):
        """The rightest column of the hitbox."""
        return self._minimal_rect.right

    @property
    def top(self):
        """The toppest row of the hitbox."""
        return self._minimal_rect.top

    @property
    def bottom(self):
        """The bottomest row of the hitbox."""
        return self._minimal_rect.bottom
