"""The KeyMapper class is used to map inputs into mapper values."""

from ...io_.utils import get_file
import json
import pygame

KEYMAP_PATH = 'keymap.json'

class KeyMapper:
    """
    The key mapper is used to map the keybord keys into actions.
    It contains a dictionnary of pygame.types : string, that map a type of event into a string.
    The string is an action, the pygame.type is a str(int).
    The current mapping is store in the dynamic data/keymap.json file.
    """

    def __init__(self) -> None:
        
        with open(get_file('data', KEYMAP_PATH, dynamic=True)) as f:
            _key_map_dict: dict = json.load(f)
            self._key_map_dict = {}
            for key, action in _key_map_dict:
                if not key.isdigit() and hasattr(pygame, key):
                    self._key_map_dict[getattr(pygame, key)] = action
                else:
                    self._key_map_dict[key] = action
            self.reverse_mapping = self.get_reversed_mapping()

    def new_key(self, key: int, value: str):
        """Modify a key map."""
        # Modify the current dict
        self._key_map_dict[str(key)] = value
        # Modify the file
        with open(get_file('data', KEYMAP_PATH, dynamic=True), 'w') as f:
            json.dump(self._key_map_dict, f)
        self.reverse_mapping = self.get_reversed_mapping()

    def get(self, key: int):
        """Get the action associated with the key."""
        if str(key) in self._key_map_dict:
            return self._key_map_dict[str(key)]
        raise ValueError(f"No such key {key}.")

    def get_reversed_mapping(self):
        """Get all the defined keys and the actions."""
        reversed_mapping = {}
        for key, action in self._key_map_dict.items():
            if action in reversed_mapping:
                reversed_mapping[action].append(key)
            else:
                reversed_mapping[action] = []
        return reversed_mapping
        