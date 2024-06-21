from ..utils import get_file
from .file import File
import pygame

class SoundFile(File):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file('assets/sounds', path)

    def get(self):
        return pygame.mixer.Sound(self.full_path)