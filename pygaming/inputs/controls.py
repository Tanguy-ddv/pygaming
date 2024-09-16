"""The Controls class is used to map inputs into mapper values."""

import pygame
from ..settings import Settings

class Controls:
    """
    The controls is used to map the keybord keys into actions.
    It contains a dictionnary of pygame.types : string, that map a type of event into a string.
    The string is an action, the pygame.type is a str(int).
    The current mapping is store in the dynamic data/keymap.json file.
    """

    def __init__(self, settings: Settings) -> None:

        self._key_map_dict: dict[str, str] = {}
        self._reverse_mapping = {}
        self._settings = settings
        self._previous_controls = self._settings.controls
        self._update_settings()

    def get_reverse_mapping(self):
        """
        Get the reverse control mapping.

        Returns:
        -----
        reverse_mapping: dict[str, list[str]]. The keys are the actions, the values the list of event that would trigger it.
        """
        if self._previous_controls != self._settings.controls:
            self._update_settings()
        return self._reverse_mapping

    def _update_settings(self):
        """Update the key map dict with the current settings."""
        controls = self._settings.controls
        self._key_map_dict = {}
        for key, action in controls.items():
            if not key.isdigit() and hasattr(pygame, key):
                self._key_map_dict[str(getattr(pygame, key))] = action
            else:
                self._key_map_dict[key] = action

        self._reverse_mapping = self._get_reversed_mapping()

    def _get_reversed_mapping(self):
        """Get all the defined keys and the actions."""
        reversed_mapping = {}
        for key, action in self._key_map_dict.items():
            if action in reversed_mapping:
                reversed_mapping[action].append(key)
            else:
                reversed_mapping[action] = [key]
        return reversed_mapping
