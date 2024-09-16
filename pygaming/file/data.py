"""The data submodule of file is an abstract class used to represent the different types of data stored by the game."""
from abc import ABC, abstractmethod
from .file import File, get_file

class DataFile(File, ABC):
    """
    Abstract class for files of any type of data.
    Use this class to create file that are specific for the
    different type of data you store.
    e.g: player stored as .json, stats stored as .csv,
    places, objects, environements stored with custom extensions...
    """

    def __init__(self, path: str, dynamic: bool = False) -> None:
        File.__init__(self, path)
        ABC.__init__(self)
        self.full_path = get_file('data', path, dynamic)

    @abstractmethod
    def get(self):
        """Return the object transformed with the file."""
