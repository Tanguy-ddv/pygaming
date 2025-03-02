"""The config class is used to interact with the config file."""
from .file import load_json_file

class Config:
    """
    The config class is used to interact with the config file.
    It store several constants of the game: screen dimension, default language, default cursor, ...
    """

    def __init__(self) -> None:
        self._data, _ = load_json_file("config.json")

    def get(self, key: str, default=None):
        """Get the value of the config attribute"""
        return self._data.get(key, default)

    @property
    def dimension(self):
        """Return the dimension of the window in px x px."""
        return self.get("screen", (800, 600))

    @property
    def timeout(self):
        """Return the time before timeout on connexion."""
        return self.get("timeout", self.get("broadcast_period", 500)/1000)

    @property
    def default_language(self):
        """Return the default language."""
        return self.get("default_language", "en_US")

    @property
    def default_cursor(self):
        """Return the default cursor."""
        return self.get("default_cursor", "SYSTEM_CURSOR_ARROW")

    @property
    def game_name(self):
        """Return the name of the game."""
        return self.get("name", "My Game")

    @property
    def server_port(self):
        """Return the server port of the game."""
        return self.get("server_port", 50505)

    @property
    def max_communication_length(self):
        """Return the maximum length of a communication of the game."""
        return self.get("max_communication_length", 2048)

    def get_widget_key(self, action):
        """Return the key that would trigger the widget action."""
        return self._data["widget_keys"].get(action, False)
