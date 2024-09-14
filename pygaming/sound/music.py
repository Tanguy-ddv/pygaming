"""The Jukebox class is used to manage the musics."""

import pygame
from ..file import MusicFile
from ..settings import Settings

class Jukebox:
    """The Jukebox is used to manage the musics."""

    def __init__(self, settings: Settings) -> None:
        
        self._loop_instant = 0
        self._playing = False
        self._settings = settings
    
    def stop(self):
        """Stop the music currently playing."""
        pygame.mixer.music.stop()
        self._playing = False
    
    def play(self, music_file: MusicFile):
        """Play the music."""
        path, self._loop_instant = music_file.get()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(0)
        self._playing = True

    def update(self):
        """This function should be called at the end of every gameloop to make the function loop."""

        pygame.mixer.music.set_volume(self._settings.volumes['main']*self._settings.volumes['music'])
        if not pygame.mixer.music.get_busy() and self._playing and self._loop_instant is not None:
            pygame.mixer.music.play(0, self._loop_instant)
