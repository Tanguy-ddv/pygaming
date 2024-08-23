from .file import File, get_file
import json

class MusicFile(File):
    """Represent the file of a music."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.full_path = get_file('musics', name)
        with open(get_file('musics', 'loop_times.json')) as f:
            all_loop_times: dict = json.load(f)
            if name in all_loop_times:
                self.loop_time = all_loop_times[name]
            else:
                self.loop_time = None
    
    def get(self):
        return self.full_path, self.loop_time
