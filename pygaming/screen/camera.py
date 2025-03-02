"""The window module contains the window class."""
import pygame
import numpy as np
from pygamecv.effect import saturate, desaturate, darken, lighten, shift_hue
from .anchors import TOP_LEFT, Anchor
from .art import mask as mask_
from ..settings import Settings

def _set_alpha(surface: pygame.Surface, matrix: np.ndarray):
    surface = surface.convert_alpha()
    alpha = pygame.surfarray.pixels_alpha()
    alpha[:] = (255 - matrix*255).astype(np.int8)
    return surface

class Camera(pygame.Rect):
    """
    Camera are used to to define the part of the frame that will be shown on the screen.
    They can also apply some effects on the render, through masks.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        anchor: Anchor = TOP_LEFT,
        darken_mask: mask_.Mask = None,
        lighten_mask: mask_.Mask = None,
        saturate_mask: mask_.Mask = None,
        desaturate_mask: mask_.Mask = None,
        hide_mask: mask_.Mask = None,
        shift_hue_mask: mask_.Mask = None
    ):
        """
        Create a new camera.

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

    def get_surface(self, surface: pygame.Surface, settings: Settings):
        """Return the surface extracted by the camera."""
        surface = surface.subsurface(self)
        for mask, func in zip([
            self.darken_mask, self.lighten_mask, self.desaturate_mask, self.saturate_mask, self.shift_hue_mask
        ], [
            darken, lighten, desaturate, saturate, shift_hue
        ]):
            if mask is not None:
                mask.load(*surface.get_size(), **settings)
                func(surface, mask.matrix)
        if self.hide_mask is not None:
            self.hide_mask.load(*surface.get_size(), **settings)
            return _set_alpha(surface, self.hide_mask.matrix)
        else:
            return surface
