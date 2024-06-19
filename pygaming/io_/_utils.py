from typing import Literal
import sys
import os
import json


def get_file(folder: Literal['data', 'musics', 'sounds', 'images', 'videos', 'fonts'], file: str, dynamic : bool = False):
    """
    Return the full path of the file.
    
    params:
    ----
    folder: the folder of the file
    file: the name of the file.
    dynamic: if False, get the file from the temporary folder of the app. If True, from the place where the file dynamic files are saved
    
    Dynamic files are the ones that might be modified during the game and that should be saved.
    Exemple of dynamic files: saves, ig_queries, logs.
    """
    if folder != 'data':
        folder = 'assets/' + folder
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        if dynamic:
            config_path = os.path.join(base_path, 'data', 'config.json')
            config_file = open(config_path,'r')
            base_path = json.load(config_file)['path_to_dynamic']
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, folder, file)