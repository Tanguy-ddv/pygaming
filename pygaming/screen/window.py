import pygame
from typing import Union
from .element import TOP_LEFT
from .mask import Mask, ALPHA, DARKEN, LIGHTEN, DESATURATE, SATURATE
from ..error import PygamingException
from ..color import ColorLike, Color

_EFFECT_LIST = [ALPHA, DARKEN, LIGHTEN, SATURATE, DESATURATE]

class Window:
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
        mask: Mask = None,
        mask_effects: dict[str, float] = {ALPHA : 1.},
        fill_color: ColorLike = Color(0, 0, 0, 0)
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
        - mask: Mask = None. If a mask is specified, it will be applied to the image of the window
        - mask_effects: dict[str, float] = {pygaming.ALPHA, 1.}, the effects and the intensity of the effect
        that the mask will apply. If mask is None, no need for this argument.

        Examples:
        -----
        - pygaming.Window(100, 100, 70, 70, pygaming.BOTTOM_LEFT, pygaming.Circle(radius=30, center=(35, 30))) will create a window:
        The image will be displayed as a Circle, whose center is at the coordinates (35, 30) of a rectangle of shape(70, 70).
        The bottom left point of the rectangle will be display at the coordinate (100, 100) of the master.

        - pygaming.Window(100, 100, 70, 70, pygaming.BOTTOM_LEFT, pygaming.RectangleGradient(50, 50, 60, 60), {DARKEN : 0.5})
        will create a rectangle window of shape (70, 70). Inside the window, the pixels inside the rectangle of shape (50, 50) will
        not be transformed. The pixels outside of the rectangle of shape(60, 60) will be darken by 50%, the other pixels will be darken by
        a factor between 0% and 50%, as a gradient from the inner to the outer rectangle.
        """
        if DARKEN in mask_effects.keys() and LIGHTEN in mask_effects.keys():
            raise PygamingException("DARKEN and LIGHTEN cannot be effects of the same mask.")
        if SATURATE in mask_effects.keys() and DESATURATE in mask_effects.keys():
            raise PygamingException("SATURATE and DESATURATE cannot be effects of the same mask.")
        if any(key not in _EFFECT_LIST for key in mask_effects.keys()):
            raise PygamingException(f"Invalid keys for mask effects, key allowed are pygaming.ALPHA, pygaming.LIGHTEN, pygaming.DARKEN, pygaming.SATURATE, pygaming.DESATURATE")

        self._effects = mask_effects
    
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self.anchor = anchor
        self.mask = mask

        self._rect = pygame.Rect(self._x, self._y, self._width, self._height)
        self._fill_color = fill_color
    
    @property
    def coordinate(self):
        return (self._x, self._y)

    @property
    def size(self):
        return (self._width, self._height)

    def get_surface(self, surface: pygame.Surface):
        """Return the surface extracted by the window."""
        if self._width > surface.get_width() or self._height > surface.get_height():
            surf = pygame.Surface((self.size), pygame.SRCALPHA)
            surf.fill(self._fill_color)
            surf.blit(surface, (0, 0))
        else:
            surf = surface.copy()
        if self.mask:
            surface = surf.subsurface(self._rect)
            self.mask.apply(surface, self._effects)
            return surface
        else:
            return surf.subsurface(self._rect)

WindowLike = Union[Window, tuple[int, int, int, int], tuple[int, int, int, int, tuple[float, float]]]