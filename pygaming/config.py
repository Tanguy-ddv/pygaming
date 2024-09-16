"""The config class is used to interact with the config file."""
import json
from .file import get_file

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

    @property
    def dimension(self):
        """Return the dimension of the window in px x px."""
        key = "screen"
        if key in self._data:
            return self._data[key]
        return (800, 600)

    @property
    def default_language(self):
        """Return the default language."""
        key = "default_language"
        if key in self._data:
            return self._data[key]
        return "en_US"

    @property
    def default_cursor(self):
        """Return the default cursor."""
        key = "default_cursor"
        if key in self._data:
            return self._data[key]
        return "SYSTEM_CURSOR_ARROW"

    @property
    def game_name(self):
        """Return the name of the game."""
        key = "name"
        if key in self._data:
            return self._data[key]
        return "MyGame"

    @property
    def server_port(self):
        """Return the server port of the game."""
        key = "server_port"
        if key in self._data:
            return self._data[key]
        return 50505

    @property
    def max_communication_length(self):
        """Return the maximum length of a communication of the game."""
        key = "max_communication_length"
        if key in self._data:
            return self._data[key]
        return 2048
