"""The inputs class is used to manage the inputs."""

import pygame
from dataclasses import dataclass
from .key_mapper import KeyMapper
from string import ascii_letters, digits, punctuation 
ACCEPTED_LETTERS = ascii_letters + digits + punctuation + " "

class Inputs:
    """
    The inputs class is used to manage the inputs.
    check if the user clicked somewhere or if a key have been pressed by using this class.
    """

    def __init__(self) -> None:
        
        self._key_mapper = KeyMapper()
        self.clear_mouse_velocity()

    def get_characters(self):
        """Return all the letter characters a-z, digits 0-9, whitespace and punctuation."""
        return [event.unicode for event in pygame.event.get() if event.type == pygame.KEYDOWN and event.unicode in ACCEPTED_LETTERS]

    def get_quit(self):
        return any(event.type == pygame.QUIT for event in pygame.event.get())

    def get_clicks(self):
        """Return the clicks and the position."""

        return {event.button if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONDOWN] else 0 :
            Click(event.pos[0], event.pos[1], event.type == pygame.MOUSEBUTTONUP)
            for event in pygame.event.get()
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN]
        }

    def clear_mouse_velocity(self):
        """Remove the history of mouse velocity."""
        self.mouse_x = None
        self.mouse_y = None

    def get_mouse_velocity(self):
        """Return the current mouse speed."""
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                if self.mouse_x is not None and self.mouse_y is not None:
                    velocity = self.mouse_x - event.pos[0], self.mouse_y - event.pos[0]
                    self.mouse_x = event.pos[0]
                    self.mouse_y = event.pos[1]
                    return velocity

    def get_actions(self):
        """Return a dict of str: bool specifying if the action is trigger or not."""
        types = [event.type for event in pygame.event.get()]
        return {
            action : any(key in types for key in keys) 
            for action, keys in self._key_mapper.reverse_mapping}

@dataclass
class Click:
    """Represent a click with the mouse."""

    x: int # The position of the mouse on the click
    y: int 
    up: bool # True if it is a button up, False if it is a button down
