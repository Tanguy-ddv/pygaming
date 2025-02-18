"""The window module contains the window class."""
from typing import Union, Sequence
import pygame
from .anchors import TOP_LEFT
from .art import mask
from ..error import PygamingException
from ..settings import Settings

class Window(pygame.Rect):
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
        mask: mask.Mask | Sequence[mask.Mask] = None,
        mask_effects: dict[str, float] | Sequence[dict[str, float]] = {ALPHA : 100},
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
        if isinstance(mask, Sequence):
            if not isinstance(mask_effects, Sequence) or len(mask_effects) != len(mask):
                raise PygamingException(
                    f"Unmatching mask and mask effect numbers, got {len(mask)} masks and {len(mask_effects)} mask effects."
                )
        elif isinstance(mask_effects, Sequence):
            raise PygamingException("Both mask_effects and mask must be a Sequence at the same time, or be a simple element.")

        elif not mask is None:
            mask = [mask]
            mask_effects = [mask_effects]

        else: # if mask is None
            mask = []
            mask_effects = []

        for mask_eff in mask_effects:

            if DARKEN in mask_eff and LIGHTEN in mask_eff:
                raise PygamingException("DARKEN and LIGHTEN cannot be effects of the same mask.")
            if SATURATE in mask_eff and DESATURATE in mask_eff:
                raise PygamingException("SATURATE and DESATURATE cannot be effects of the same mask.")
            if any(key not in _EFFECT_LIST for key in mask_eff):
                raise PygamingException(
                    """Invalid keys for mask effects, key allowed are: 
                    pygaming.ALPHA, pygaming.LIGHTEN, pygaming.DARKEN, pygaming.SATURATE, pygaming.DESATURATE"""
                )

        self._effects = mask_effects

        self._x = x
        self._y = y
 
        self.anchor = anchor
        self.masks = mask

        super().__init__(self._x, self._y, width, height)    
    def get_at(self, pos: tuple[int, int]):
        """Return True if the point is inside the window."""
        return self.collidepoint(*pos)

    def get_surface(self, surface: pygame.Surface):
        """Return the surface extracted by the window."""

        for mask, effects in zip(self.masks, self._effects):
            mask.apply(surface, effects)

        return surface

    def update(self, loop_duration):
        """Update the masks of the window."""
        for mask in self.masks:
            mask.update(loop_duration)

    def load(self, settings: Settings):
        """Load the masks of the window."""
        for mask in self.masks:
            mask.load(settings)

    def unload(self):
        """Unload the masks of the window."""
        for mask in self.masks:
            mask.unload()

WindowLike = Union[Window, tuple[int, int, int, int], tuple[int, int, int, int, tuple[float, float]], pygame.Rect]
