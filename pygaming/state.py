"""The state module contains functions to interact with the state file."""
from typing import Any
from time import time
from .file import load_json_file, save_json_file

class State:
    """The State class contains variables that are persistent through multiple launch of the game."""

    def __init__(self):
        self._data, self._encoding = load_json_file('state.json')

    def get_state(self):
        """
        Return the current state.
        """
        return self._data

    def set_state(self, key: str, value: Any):
        """
        Set a new value for one of the entry of the state.

        Params:
        ----
        - key: str, the name of the attribute to be changed.
        - value: Any, the value to set the new attribute to.
        """

        self._data[key] = value

    def set_states(self, key_values: dict[str, Any]):
        """
        Set several new values for the state.

        Params:
        - key_values: dict, a dict of str, Any to update the state to.
        If some keys of the state are not in this dict, they are unchanged.

        """
        self._data.update(key_values)

    def increment_counter(self, counter: str):
        """
        Increment one counter saved in the state

        Params:
        - counter: str, the name of the counter to increment.
        """
        self._data[counter] += 1

    def set_time_now(self, time_variable: str):
        """
        Set a new time for the one variable

        Params:
        - time_variable: str, the name of the time variable to set to now.
        time is represent as a timestamp in ms.
        """
        self._data[time_variable] = int(time()*1000)

    def save(self):
        """Save the current state."""
        save_json_file("state.json", self._data, self._encoding)
