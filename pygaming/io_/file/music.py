from ..utils import get_file
from .file import File
import json

class MusicFile(File):
    """Represent the file of a music."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.full_path = get_file('assets/musics', name)
        with open(get_file('musics', 'loop_times.json')) as f:
            all_loop_times: dict = json.load(f)
            if name in all_loop_times:
                self.loop_time = all_loop_times[name]
            else:
                self.loop_time = 0
    
    def get(self):
        return self.full_path, self.loop_time
