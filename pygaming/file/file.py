from abc import ABC, abstractmethod
from typing import Any, Literal

import sys
import os
import json

class File(ABC):
    """Represent any type of file that would be loaded for the game: image, sounds, etc."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.full_path = None

    @abstractmethod
    def get(self) -> Any:
        """Get the object in the proper format to be used by the game."""

def get_file(folder: Literal['data', 'musics', 'sounds', 'images', 'videos', 'fonts'], file: str, permanent: bool = False):
    """
    Return the full path of the file.
    
    params:
    ----
    folder: the folder of the file
    file: the name of the file.
    permanent: if False, get the file from the temporary folder of the app. If True, from the place where the file dynamic files are saved
    
    Non-Permanent files are the ones that might be modified during the game and that should be saved.
    Exemple of non-permanent files: saves, ig_queries, logs.
    """
    if folder != 'data':
        folder = 'assets/' + folder
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        if not permanent:
            config_path = os.path.join(base_path, 'data', 'config.json')
            config_file = open(config_path,'r')
            base_path = json.load(config_file)['path']
            config_file.close()
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, folder, file)