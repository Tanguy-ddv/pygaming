"""Represent a sound in the assets/sounds folder."""

import json
import pygame
from .file import File, get_file


class SoundFile(File):
    """A SoundFile represent a sound in the assets/sounds folder."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file('sounds', path)

        with open(get_file('sounds', 'categories.json'), 'r', encoding='utf-8') as f:
            categories: dict = json.load(f)
            if path in categories:
                self.category = categories[path]
            else:
                self.category = "unavailable"

    def get(self):
        """
        Get the sound from its file.
        
        Returns:
        ----
        sound: the sound as a pygame object
        category: str, the category of the sound to be played with the proper volume.
        """
        return pygame.mixer.Sound(self.full_path), self.category
