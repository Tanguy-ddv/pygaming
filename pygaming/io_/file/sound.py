from ..utils import get_file
from .file import File
import pygame
import json

class SoundFile(File):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file('sounds', path)

        with open(get_file('sounds', 'categories.json')) as f:
            categories: dict = json.load(f)
            if path in categories:
                self.category = categories[path]
            else:
                self.category = None

    def get(self):
        return pygame.mixer.Sound(self.full_path), self.category