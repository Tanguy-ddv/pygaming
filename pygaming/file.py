"""
The file module contains the get_file function used in all File class to find the full path of the object
"""
from typing import Literal

import os
import json
from functools import lru_cache
import base64

def _open_json_file(path):
    """Open any json file, encoded with b64 or not."""
    with open(path, 'rb') as f:
        binary_data = f.read()
    try:
        json_string = binary_data.decode('utf-8')  # Attempt to decode binary to string
        return json.loads(json_string), True # If it works, the file wasn't encoded

    except (UnicodeDecodeError, json.JSONDecodeError): # Otherwise, it was
        decoded_data = base64.b64decode(binary_data)
        json_string = decoded_data.decode('utf-8')
        return json.loads(json_string), False

@lru_cache(maxsize=1)
def _get_base_path():

    config_path = os.path.join(os.path.abspath("."), 'data', 'config.json')
    return _open_json_file(config_path)[0]['path']

def get_file(folder: Literal['data', 'musics', 'sounds', 'images', 'videos', 'fonts', 'cursors'], file: str):
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

def load_json_file(file: str) -> tuple[dict, bool]:
    """Load a json file that may or may not be encoded. Return True if the file was encoded."""
    file_path = get_file('data', file)
    return _open_json_file(file_path)

def save_json_file(file: str, data: dict, encode: bool = False):
    """Save a json file as encryoted or not."""
    file_path = get_file('data', file)
    if encode:
        # Save as Base64-encoded JSON
        with open(file_path, 'wb') as f:
            encoded_data = base64.b64encode(json.dumps(data).encode('utf-8'))
            f.write(encoded_data)
    else:
        # Save as plain JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
