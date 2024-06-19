from abc import ABC, abstractmethod
from typing import Any

class File(ABC):
    """Represent any type of file that would be loaded for the game: image, sounds, etc."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.full_path = None

    @abstractmethod
    def get(self) -> Any:
        """Get the object in the proper format to be used by the game."""