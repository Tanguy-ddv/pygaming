from abc import ABC, abstractmethod
from .file import File
from .._utils import get_file

class DataFile(File, ABC):
    """
    Abstract class for files of any type of data.
    Use this class to create file that are specific for the
    different type of data you store.
    e.g: player stored as .json, stats stored as .csv,
    places, objects, environements stored with custom extensions...
    """

    def __init__(self, path: str, dynamic: bool = False) -> None:
        super().__init__(path)
        self.full_path = get_file('data', path, dynamic)
    
    @abstractmethod
    def get(self):
        """Return the object transformed with the file."""
