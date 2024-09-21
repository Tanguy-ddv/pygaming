"""AnimatedSurface is a class use to represent the a Surface that might be animated."""
from typing import List, Iterable
import pygame
from ..file import ImageFile
from ..error import PygamingException

SurfacesLike = List[pygame.Surface | ImageFile]

class AnimatedSurface:
    """An AnimatedSurface is a Surface that can be animated."""

    def __init__(
        self,
        surfaces: SurfacesLike,
        image_duration: int | list[int] = 100, # [ms]
        image_introduction: int = 0
    ) -> None:
        """
        Create the surfaces

        params:
        ----
        width: int, the width of the object.
        height: int, the hieght of the object.
        surfaces: SurfacesLike, The surfaces of the objects.
        if only one element is given, it is treated as a list of length 1
        If it is a (list of) color or a str, create a list of surface of this color with the shape (width, height)
        If it is a (list of) surface, resize the surface with (width, height)
        Can be a list of colors and surfaces, str
        image_duration: If several surfaces are given, as a list of str, color, ImageFile or Surface,
        the frame duration is the amount of time each frame is displayed before. If it is a list, it must be the same length than surfaces.
        image_introduction: int, default 0. If an integer is given (< length of surfaces), the loop does not go back to the first image but to this one.
        ex: In a platformer, the 5 first frames are the character standing in the right direction, then he walks. For this, we use a image_introduction=5
        """
        self._index = 0
        self._image_introduction = image_introduction
        self._introduction_done = False
        self._time_since_last_change = 0

        if not isinstance(surfaces, Iterable):
            raise PygamingException("The surfaces must be an iterable")

        self._surfaces: list[pygame.Surface] = []
        for bg in surfaces:
            if isinstance(bg, ImageFile):
                bg = bg.get()
            self._surfaces.append(bg)
        self._n_bg = len(surfaces)

        if not isinstance(image_duration, Iterable):
            image_duration = [image_duration]*self._n_bg
        elif len(image_duration) != self._n_bg:
            raise PygamingException(
                f"The length of the frame duration list ({len(image_duration)}) does not match the len of the backroung list ({self._n_bg}))"
            )
        self._image_durations = image_duration
        if self._image_introduction > self._n_bg:
            raise PygamingException(
                f"The image introduction parameters must be between 0 and {self._n_bg}, but got {self._image_introduction}"
            )

    def update_animation(self, loop_duration: float):
        """Update the background"""
        if self._n_bg > 1:
            self._time_since_last_change += loop_duration
            if self._time_since_last_change >= self._image_durations[self._index]:
                self._time_since_last_change = 0
                if not self._introduction_done:
                    self._index = (self._index+1)%self._n_bg
                    if self._index > self._image_introduction:
                        self._introduction_done = True
                else:
                    self._index = (self._index+1 - self._image_introduction)%(self._n_bg - self._image_introduction) + self._image_introduction

    @property
    def height(self):
        """Return the height of the surface, which is the height of the first surface."""
        return self._surfaces[0].get_height()

    @property
    def width(self):
        """Return the width of the surface, which is the width of the first surface."""
        return self._surfaces[0].get_width()

    def reset(self):
        """Reset the counts of the animations."""
        self._index = 0
        self._introduction_done = False
        self._time_since_last_change = 0

    def get(self):
        """
        Return the background.
        """
        self._index = self._index%self._n_bg
        return self._surfaces[self._index].copy()

    def copy(self):
        """Return a copy of the surface."""
        return AnimatedSurface([s.copy() for s in self._surfaces], self._image_durations.copy(), self._image_introduction)

def make_rounded_rectangle(color: pygame.Color | str, width: int, height: int):
    """Make a rectange with half circles at the start and end."""
    if isinstance(color, str):
        if color in pygame.color.THECOLORS:
            color = pygame.color.THECOLORS[color]
        else:
            color = pygame.Color(0,0,0,255)

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(height//2, 0, width - height, height)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.circle(surface, color, (height//2, height//2), height//2)
    pygame.draw.circle(surface, color, (width - height//2, height//2), height//2)
    return surface
