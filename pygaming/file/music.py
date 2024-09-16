"""A MusicFile represent the file of a music."""

import json
from .file import File, get_file

class MusicFile(File):
    """Represent the file of a music in the assets/musics folder."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.full_path = get_file('musics', name)
        with open(get_file('musics', 'loop_times.json'), encoding='utf-8') as f:
            all_loop_times: dict = json.load(f)
            if name in all_loop_times:
                self.loop_time = all_loop_times[name]
            else:
                self.loop_time = None

    def get(self):
        """
        Get the music.
        
        Returns:
        full_path: str, the path to the music
        loop_time: int, the loop time.
        """
        return self.full_path, self.loop_time
