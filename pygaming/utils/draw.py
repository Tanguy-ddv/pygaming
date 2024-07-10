"""The utils module contains several functions."""

import pygame

def make_background(background: pygame.Surface | pygame.Color | None, width: int, height: int, reference: pygame.Surface | None):
    """
    Create a background:
    if background is a surface, return the rescaled surface.
    if the background is a color, return a rectangle of this color.
    if the background is None, return a copy of the reference.
    if the reference and the background are None, raise an Error.
    We assume here that the reference have the shape (width, height)
    """

    if background is None:
        if reference is None:
            raise TypeError("The reference must be a surface if the background is None.")
        return reference.copy()
    elif isinstance(background, pygame.Color):
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill(background)
        return bg
    else:
        return pygame.transform.scale(background, (width, height))

def make_rounded_rectangle(color: pygame.Color, width: int, height: int):
    """Make a rectange with half circles at the start and end."""
    background = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(height//2, 0, width - height, height)
    pygame.draw.rect(background, color, rect)
    pygame.draw.circle(background, color, (height//2, height//2), height//2)
    pygame.draw.circle(background, color, (width - height//2, height//2), height//2)
    return background
