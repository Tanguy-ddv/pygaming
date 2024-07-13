"""The Jukebox class is used to manage the musics."""

import pygame
from ..file import MusicFile
import json
from .._settings import Settings

# TODO: do the same for the soundbox, keymapper
# TODO: do the same with the texts but with update_with_config and update_with_settings
# TODO: do the same with the screen but with update_with_config and update_with_settings, create a screen class.
# TODO: rename the keymapper class controls

class Jukebox:
    """The Jukebox is used to manage the musics."""

    def __init__(self) -> None:
        
        self.volume = 1
        self._loop_instant = 0
        self._playing = False
    
        pygame.mixer.music.set_volume(self.volume)
    
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
    
    def update_settings(self, settings: Settings):
        """Update the volume with the settings."""
        volumes = settings.volumes
        self.volume = volumes['main']*volumes['music']
