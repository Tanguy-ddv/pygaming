from .._utils import get_file
from .file import File

class MusicFile(File):
    """Represent the file of a music."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.full_path = get_file('assets/musics', name)
    
    def get(self):
        return self.full_path
