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

    def __init__(self) -> None:
        """Create the keyboard."""
        self.controls = None
        self.event_list: list[pygame.event.Event] = []
        self._control_mapping = {}
        self.actions_pressed = {}
        self.actions_down = {}
        self.actions_up = {}

    def load_controls(self, settings: Settings, config: Config, phase_name: str):
        """Load the new controls"""
        self.controls = Controls(settings, config, phase_name)
        self._control_mapping = self.controls.get_reversed_mapping()
        self.udpate_actions_down()
        self.update_actions_up()
        self.actions_pressed = self.actions_down

    def update_settings(self):
        """Update the controls."""
        self.controls.update_settings()
        self._control_mapping = self.controls.get_reversed_mapping()

    def update(self, event_list: list[pygame.event.Event]):
        """Update the keyboard with the event list."""
        self.event_list = event_list
        self.update_actions_up()
        self.udpate_actions_down()
        self.update_actions_pressed()

    def get_characters(self, extra_characters: str = '', forbid_characters: str = ''):
        """
        Return all the letter characters a-z, digits 0-9, whitespace, punctuation and extra caracters
        (except forbidden characters) typed by the player.
        """
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

    def udpate_actions_down(self):
        """
        Return a dict of str: bool specifying if the action is triggered or not.
        The action is triggered if the user just pressed the key.
        """
        types = [event.key for event in self.event_list if event.type == pygame.KEYDOWN]
        self.actions_down = {
            action : any(int(key) in types for key in keys)
            for action, keys in self._control_mapping.items()}

    def update_actions_up(self):
        types = [event.key for event in self.event_list if event.type == pygame.KEYUP]
        self.actions_up = {
            action : any(int(key) in types for key in keys)
            for action, keys in self._control_mapping.items()}

    def update_actions_pressed(self):
        """
        Update the dict of str: bool specifying if the action is triggered or not.
        The action is triggered if the user is pressing the key.
        """
        for key, upped in self.actions_down.items():
            if upped:
                self.action_pressed[key] = False
        for key, upped in self.actions_up.items():
            if upped:
                self.action_pressed[key] = True
