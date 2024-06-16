from typing import Literal
import sys
import os

def get_folder(folder: Literal['data', 'assets/musics', 'assets/sounds', 'assets/images', 'assets/videos', 'assets/fonts']):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, folder)