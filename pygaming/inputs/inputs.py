"""The inputs class is used to manage the inputs."""

import pygame
from dataclasses import dataclass
from .controls import Controls
from string import ascii_letters, digits, punctuation
from ..settings import Settings
_ACCEPTED_LETTERS = ascii_letters + digits + punctuation + " "

class Inputs:
    """
    The inputs class is used to manage the inputs.
    check if the user clicked somewhere or if a key have been pressed by using this class.
    """

    def __init__(self, settings: Settings) -> None:
        
        self.controls = Controls(settings)
        self.clear_mouse_velocity()
        self.event_list: list[pygame.event.Event] = []
    
    def update(self):
        """Get the current events."""
        self.event_list = pygame.event.get()

    def get_characters(self, extra_characters: str = ''):
        """Return all the letter characters a-z, digits 0-9, whitespace and punctuation."""
        return [event.unicode for event in self.event_list if event.type == pygame.KEYDOWN and event.unicode and event.unicode in _ACCEPTED_LETTERS + extra_characters]

    @property
    def quit(self):
        return any(event.type == pygame.QUIT for event in self.event_list)

    def get_clicks(self, frame_abs_x: int = 0, frame_abs_y: int = 0):
        """Return the clicks and the position."""

        return {event.button if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP] else 0 :
            Click(event.pos[0] - frame_abs_x, event.pos[1] - frame_abs_y, event.type == pygame.MOUSEBUTTONUP)
            for event in self.event_list
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]
        }

    def clear_mouse_velocity(self):
        """Remove the history of mouse velocity."""
        self.mouse_x = None
        self.mouse_y = None
    
    def get_keydown(self, key: int):
        """Return true if the key is just pressed down."""
        for event in self.event_list:
            if event.type == pygame.KEYDOWN and event.key == key:
                return True
        return False

    def get_keyup(self, key: int):
        """Return true if the key is just unpressed."""
        for event in self.event_list:
            if event.type == pygame.KEYUP and event.key == key:
                return True
        return False

    def get_mouse_velocity(self):
        """Return the current mouse speed."""
        for event in self.event_list:
            if event.type == pygame.MOUSEMOTION:
                if self.mouse_x is not None and self.mouse_y is not None:
                    velocity = event.pos[0] - self.mouse_x, event.pos[1] - self.mouse_y
                    self.mouse_x = event.pos[0]
                    self.mouse_y = event.pos[1]
                    return velocity
                self.mouse_x = event.pos[0]
                self.mouse_y = event.pos[1]
                return 0,0
        self.mouse_x = None
        self.mouse_y = None
        return 0,0

    def get_actions(self):
        """Return a dict of str: bool specifying if the action is trigger or not."""
        types = [event.key for event in self.event_list if event.type == pygame.KEYDOWN]
        return {
            action : any(int(key) in types for key in keys)
            for action, keys in self.controls.reverse_mapping.items()}

    def get_arrows(self):
        return [(event.type, event.key) for event in self.event_list if hasattr(event, 'key') and event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]]



@dataclass
class Click:
    """Represent a click with the mouse."""

    x: int # The position of the mouse on the click
    y: int 
    up: bool # True if it is a button up, False if it is a button down
