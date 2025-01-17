"""
The file module contains the get_file function used in all File class to find the full path of the object
"""
from typing import Literal

import os
import json
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_base_path():

    config_path = os.path.join(os.path.abspath("."), 'data', 'config.json')
    config_file = open(config_path,'r', encoding='utf-8')
    base_path = json.load(config_file)['path']
    config_file.close()

    return base_path

def get_file(folder: Literal['data', 'musics', 'sounds', 'images', 'videos', 'fonts'], file: str):
    """
    Return the full path of the file.
    
    params:
    ----
    - folder: the folder of the file
    - file: the name of the file.
    """

    base_path = _get_base_path()

    if folder != 'data':
        return os.path.join(base_path, 'assets', folder, file).replace('\\', '/')
    else:
        return os.path.join(base_path, folder, file).replace('\\', '/')

def get_state():
    """
    Return the content of the state file.
    """
    state_path = get_file('data', 'state.json')
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    return current_state

def set_state(key, value):
    """
    Set a new value for one of the entry of the state.
    """
    state_path = get_file('data', 'state.json')
    with open(state_path, 'r', encoding='utf-8') as f:
        current_state: dict = json.load(f)
    current_state[key] = value
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=4)
