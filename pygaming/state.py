"""The state module contains functions to interact with the state file."""
import json
import time
from functools import lru_cache
from typing import Any

from .file import get_file

@lru_cache(maxsize=1)
def _get_state_path():
    """
    Get the path of the state file.
    """
    return get_file('data', 'state.json')

def get_state():
    """
    Return the content of the state file.
    """
    state_path = _get_state_path()
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    return current_state

def set_state(key: str, value: Any):
    """
    Set a new value for one of the entry of the state.

    Params:
    ----
    - key: str, the name of the attribute to be changed.
    - value: Any, the value to set the new attribute to.
    """
    state_path = _get_state_path()
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    current_state[key] = value
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=4)

def set_states(key_values: dict[str, Any]):
    """
    Set several new values for the state.

    Params:
    - key_values: dict, a dict of str, Any to update the state to.
    If some keys of the state are not in this dict, they are unchanged.

    """
    state_path = _get_state_path()
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    current_state.update(key_values)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=4)

def increment_counter(counter: str):
    """
    Increment one counter saved in the state

    Params:
    - counter: str, the name of the counter to increment.
    """
    state_path = _get_state_path()
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    current_state[counter] += 1
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=4)

def set_time_now(time_variable: str):
    """
    Set a new time for the one variable

    Params:
    - time_variable: str, the name of the time variable to set to now.
    time is represent as a timestamp in ms.
    """
    state_path = _get_state_path()
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    current_state[time_variable] = int(time.time()*1000)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=4)
