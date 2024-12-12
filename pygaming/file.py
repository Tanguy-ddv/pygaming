"""
The file module contains the get_file function used in all File class to find the full path of the object
"""
from typing import Literal

import sys
import os
import json

def get_file(folder: Literal['data', 'musics', 'sounds', 'images', 'videos', 'fonts'], file: str, permanent: bool = False):
    """
    Return the full path of the file.
    
    params:
    ----
    - folder: the folder of the file
    - file: the name of the file.
    - permanent: if False, get the file from the temporary folder of the app. If True, from the place where the file dynamic files are saved
    
    Non-Permanent files are the ones that might be modified during the game and that should be saved.
    Exemple of non-permanent files: saves, ig_queries, logs.
    """
    if folder != 'data':
        folder = 'assets/' + folder
    if hasattr(sys, '_MEIPASS'):
        #pylint: disable=protected-access
        base_path = sys._MEIPASS
        if not permanent:
            config_path = os.path.join(base_path, 'data', 'config.json')
            config_file = open(config_path,'r', encoding='utf-8')
            base_path = json.load(config_file)['path']
            config_file.close()
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, folder, file).replace('\\', '/')
