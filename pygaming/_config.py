"""The config class is used to interact with the config file."""
from file import get_file
import json

class Config:
    """The config class is used to interact with the config file."""

    def __init__(self) -> None:
        path = get_file('data', 'config.json', True)
        file = open(path, 'r', encoding='utf-8')
        self._data = json.load(file)
        file.close()

    def get(self, key: str):
        """Get the value of the config attribute"""
        if key in self._data:
            return self._data[key]
        return None
    
    def get_language(self):
        """Return the default language."""
        key = "default_language"
        if key in self._data:
            return self._data[key]
        return "en_US"
    
    def get_cursor(self):
        """Return the default cursor."""
        key = "default_cursor"
        if key in self._data:
            return self._data[key]
        return "SYSTEM_CURSOR_ARROW"

    def get_name(self):
        """Return the name of the game."""
        key = "name"
        if key in self._data:
            return self._data[key]
        return "MyGame"


