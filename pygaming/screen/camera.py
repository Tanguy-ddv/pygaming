"""The window module contains the window class."""
import pygame
import numpy as np
from pygamecv.effect import saturate, desaturate, darken, lighten, shift_hue
from .anchors import TOP_LEFT
from .art import mask
from ..settings import Settings

def _set_alpha(surface: pygame.Surface, matrix: np.ndarray):
    surface = surface.convert_alpha()
    alpha = pygame.surfarray.pixels_alpha()
    alpha[:] = (255 - matrix*255).astype(np.int8)
    return surface

class Camera(pygame.Rect):
    """
    A window represent a portion of the screen, or of another frame.
    it is used to define the position of a Frame.
    The most basic windows are rectangles, windows can also have masks
    to apply effects on the image shown on the screen.

    If the mask is bigger than the frame itself, the remaining is filled with a given color.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        anchor: tuple[float, float] = TOP_LEFT,
        darken_mask: mask.Mask = None,
        lighten_mask: mask.Mask = None,
        saturate_mask: mask.Mask = None,
        desaturate_mask: mask.Mask = None,
        hide_mask: mask.Mask = None,
        shift_hue_mask: mask.Mask = None
    ):
        """
        Create a new mask.

        Params:
        ----
        - x: int, the x coordinate of the anchor on the parent.
        - y: int, the y coordinate of the anchor on the parent.
        - width: int, the width of the window.
        - height: int, the height of the window.
        - anchor: the anchor point in % of the width and height. 
        """
        
        self._x = x
        self._y = y
 
        self.anchor = anchor

        super().__init__(self._x, self._y, width, height)
        self.topleft = self._x - self.width*self.anchor[0], self._y - self.height*self.anchor[1]

        self.darken_mask = darken_mask
        self.lighten_mask = lighten_mask
        self.desaturate_mask = desaturate_mask
        self.hide_mask = hide_mask
        self.saturate_mask = saturate_mask
        self.shift_hue_mask = shift_hue_mask

    def get_at(self, pos: tuple[int, int]):
        """Return True if the point is inside the window."""
        return self.collidepoint(*pos)

    def get_surface(self, surface: pygame.Surface, settings: Settings):
        """Return the surface extracted by the window."""
        for mask, func in zip([
            self.darken_mask, self.lighten_mask, self.desaturate_mask, self.saturate_mask, self.shift_hue_mask
        ], [
            darken, lighten, desaturate, saturate, shift_hue
        ]):
            if mask is not None:
                mask.load(*surface.get_size(), **settings.data())
                func(surface, mask.matrix)
        if self.hide_mask is not None:
            self.hide_mask.load(*surface.get_size(), **settings.data())
            return _set_alpha(surface, self.hide_mask.matrix)
        else:
            return surface
