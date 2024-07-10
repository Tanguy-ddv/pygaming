"""The Jukebox class is used to manage the musics."""

import pygame
from ..file import get_file, MusicFile
import json

SETTINGS_PATH = 'settings.json'

class Jukebox:
    """The Jukebox is used to manage the musics."""

    def __init__(self) -> None:
        
        with open(get_file('data', SETTINGS_PATH, dynamic=True)) as f:
            volumes = json.load(f)['volume']
            self.main_volume = volumes['main']
            self.music_volume = volumes['music']
        self._loop_instant = 0
        self._playing = False
    
        pygame.mixer.music.set_volume(self.main_volume*self.music_volume)
    
    def stop(self):
        """Stop the music currently playing."""
        pygame.mixer.music.stop()
        self._playing = False
    
    def play(self, music_file: MusicFile):
        """Play the music."""
        path, self.loop_instant = music_file.get()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(0)
        self._playing = True

    def update(self):
        """This function should be called at the end of every gameloop to make the function loop."""
        if not pygame.mixer.music.get_busy() and self._playing:
            pygame.mixer.music.play(0, self.loop_instant)
    
    def _save_volumes(self):
        """Save the volumes in the config file."""

        with open(get_file('data', SETTINGS_PATH, dynamic=True)) as f:
            config = json.load(f)
            config['volume']['main'] = self.main_volume
            config['volume']['music'] = self.music_volume

        with open(get_file('data', SETTINGS_PATH, dynamic=True), 'w') as f:
            json.dump(config, f)

    def set_main_volume(self, volume):
        """Set the new main volume."""
        self.main_volume = volume
        pygame.mixer.music.set_volume(self.main_volume*self.music_volume)
        self._save_volumes()

    def set_music_volume(self, volume):
        """Set the new musique volume."""
        self.music_volume = volume
        pygame.mixer.music.set_volume(self.main_volume*self.music_volume)
        self._save_volumes()

