"""Contains a class to manage the backgrounds of a widget or any object."""
from typing import Union, List, Iterable
import pygame
from ..file import ImageFile
from ..error import PygamingException

BackgroundLike = Union[str, pygame.Surface, pygame.Color, ImageFile]
BackgroundsLike = Union[List[BackgroundLike], BackgroundLike]

class Backgrounds:
    """The backgrounds of an element is set of surfaces to display as the image, or the background image of an element."""

    def __init__(
        self,
        width: int,
        height: int,
        backgrounds: BackgroundsLike,
        image_duration: int | list[int] = 100, # [ms]
        image_introduction: int = 0
    ) -> None:
        """
        Create the backgrounds

        params:
        ----
        width: int, the width of the object.
        height: int, the hieght of the object.
        backgrounds: BackgroundsLike, The backgrounds of the objects.
        if only one element is given, it is treated as a list of length 1
        If it is a (list of) color or a str, create a list of surface of this color with the shape (width, height)
        If it is a (list of) surface, resize the surface with (width, height)
        Can be a list of colors and surfaces, str
        image_duration: If several backgrounds are given, as a list of str, color, ImageFile or Surface,
        the frame duration is the amount of time each frame is displayed before. If it is a list, it must be the same length than backgrounds.
        image_introduction: int, default 0. If an integer is given (< length of backgrounds), the loop does not go back to the first image but to this one.
        ex: In a platformer, the 5 first frames are the character standing in the right direction, then he walks. For this, we use a image_introduction=5
        """     
        self._index = 0
        self._image_introduction = image_introduction
        self._introduction_done = False
        self._time_since_last_change = 0

        if not isinstance(backgrounds, Iterable) or isinstance(backgrounds, str):
            backgrounds = [backgrounds]
        self._backgrounds: list[pygame.Surface] = []
        for bg in backgrounds:
            self._backgrounds.append(make_background(bg, width, height))
        self._n_bg = len(backgrounds)

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
                    if self._index > self._image_durations:
                        self._introduction_done = True
                else:
                    self._index = (self._index+1)%(self._n_bg - self._image_introduction) + self._image_introduction

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
        return self._backgrounds[self._index].copy()

def make_background(background: BackgroundLike, width: int, height: int):
    """
    Create a background:
    if background is a Surface or an ImageFile, return the rescaled surface.
    if the background is a Color, return a rectangle of this color.
    if the background is None, return a copy of the reference.
    if the reference and the background are None, raise an Error.
    We assume here that the reference have the shape (width, height)
    """

    if isinstance(background, str):
        if background in pygame.color.THECOLORS:
            background = pygame.color.THECOLORS[background]
        elif background.startswith('#'):
            background = pygame.Color(background)
        else:
            print(f"'{background}' is not a color, replaced by white.")
            background = pygame.Color(255,255,255,255)

    elif isinstance(background, ImageFile):
        background = background.get((width, height))

    if isinstance(background, (pygame.Color, tuple)):
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill(background)
        return bg

    elif isinstance(background, pygame.Surface):
        return pygame.transform.scale(background, (width, height))

    raise PygamingException(f"Please use a str, pygame.Surface, pygame.Color or an ImageFile for the background, got a {type(background)}")

def make_rounded_rectangle(color: pygame.Color | str, width: int, height: int):
    """Make a rectange with half circles at the start and end."""
    if isinstance(color, str):
        if color in pygame.color.THECOLORS:
            color = pygame.color.THECOLORS[color]
        else:
            color = pygame.Color(0,0,0,255)

    background = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(height//2, 0, width - height, height)
    pygame.draw.rect(background, color, rect)
    pygame.draw.circle(background, color, (height//2, height//2), height//2)
    pygame.draw.circle(background, color, (width - height//2, height//2), height//2)
    return background
