"""The KeyMapper class is used to map inputs into mapper values."""

from ...io_.utils import get_file
import json

__KEYMAP_PATH = 'keymap.json'

class KeyMapper:

    def __init__(self) -> None:
        
        with open(get_file('data', __KEYMAP_PATH, dynamic=True)) as f:
            self._key_map_dict: dict = json.load(f)

    def new_key(self, key: int, value: str):
        """Modify a key map"""
        self._key_map_dict[str(key)] = value
        with open(get_file('data', __KEYMAP_PATH, dynamic=True), 'w') as f:
            json.dump(self._key_map_dict, f)

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
        