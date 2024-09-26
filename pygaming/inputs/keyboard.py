"""The keyboard module contains the keyboard, used to represent the keyboard inputs."""
from string import ascii_letters, digits, punctuation
from typing import Iterable
import pygame
from .controls import Controls
from ..settings import Settings
from ..config import Config

_ACCEPTED_LETTERS = ascii_letters + digits + punctuation + " "

class Keyboard:
    """The keyboard class is used to manage the keyboard inputs."""

    def __init__(self, settings: Settings, config: Config) -> None:
        """Create the keyboard."""
        self.controls = Controls(settings, config)
        self.event_list: list[pygame.event.Event] = []
        self.action_pressed = self.get_actions_down()

    def update(self, event_list: list[pygame.event.Event]):
        """Update the keyboard with the event list."""
        self.event_list = event_list
        for key, upped in self.get_actions_up().items():
            if upped:
                self.action_pressed[key] = False
        for key, upped in self.get_actions_down().items():
            if upped:
                self.action_pressed[key] = True

    def get_characters(self, extra_characters: str = '', forbid_characters: str = ''):
        """Return all the letter characters a-z, digits 0-9, whitespace, punctuation and extra caracters."""
        if not isinstance(extra_characters, str) and isinstance(extra_characters, Iterable):
            extra_characters = ''.join(extra_characters)
        return [
            event.unicode for event in self.event_list
            if (event.type == pygame.KEYDOWN
                and event.unicode
                and event.unicode in _ACCEPTED_LETTERS + extra_characters
                and not event.unicode in forbid_characters
                )
        ]

    def get_actions_down(self):
        """Return a dict of str: bool specifying if the action is triggered or not. The action is triggered if the user just pressed the key."""
        types = [event.key for event in self.event_list if event.type == pygame.KEYDOWN]
        return {
            action : any(int(key) in types for key in keys)
            for action, keys in self.controls.get_reverse_mapping().items()}

    def get_actions_up(self):
        """Return a dict of str: bool specifying if the action is triggered or not. The action is triggered if the user just unpressed the key."""
        types = [event.key for event in self.event_list if event.type == pygame.KEYUP]
        return {
            action : any(int(key) in types for key in keys)
            for action, keys in self.controls.get_reverse_mapping().items()}
    
    def get_actions_press(self):
        """Return a dict of str: bool specifying if the action is triggered or not. The action is triggered if the user just unpressed the key."""
        return self.action_pressed