"""The utils module contains several functions."""

from ..io_.utils import get_file
import json
from ..utils.color import Color
import pygame

__CONFIG_FILE = get_file('data', 'config.json', dynamic=True)


def get_default_cursor():
    """Get the default cursor defined in the config file."""
    with open(__CONFIG_FILE, 'r') as f:
        default_cursor = json.load(f)['default_cursor']
    if hasattr(pygame, default_cursor):
        return pygame.Cursor(getattr(pygame, default_cursor))
    elif hasattr(pygame.cursors, default_cursor):
        return getattr(pygame.cursors, default_cursor)
    else:
        return pygame.Cursor()

def make_background(background: pygame.Surface | Color | None, width: int, height: int, reference: pygame.Surface | None):
    """
    Create a background:
    if background is a surface, return the rescaled surface.
    if the background is a color, return a rectangle of this color.
    if the background is None, return a copy of the reference.
    if the reference and the background are None, raise an Error.
    """

    if background is None:
        if reference is None:
            raise TypeError("The reference must be a surface.")
        return reference.copy()
    elif isinstance(background, Color):
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill(background.to_RGBA())
        return bg
    else:
        return pygame.transform.scale(background, (width, height))

