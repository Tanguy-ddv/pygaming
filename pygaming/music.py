"""The Jukebox class is used to manage the musics."""

from random import shuffle
import pygame
from .settings import Settings
from .file import get_file

_LOOPS = 'loops'
_PLAYLIST = 'playlist'

class Jukebox:
    """The Jukebox is used to manage the musics."""

    def __init__(self, settings: Settings) -> None:

        self._loop_instant = 0
        self._playing = False
        self._settings = settings
        self._loops_or_playlist = _LOOPS
        self._playlist_idx = 0
        self._playlist_playing = []

    def stop(self):
        """Stop the music currently playing."""
        pygame.mixer.music.stop()
        self._playing = False

    def pause(self):
        """Pause the music currently playing."""
        pygame.mixer.music.pause()
        self._playing = False
    
    def unpause(self):
        """Resume the music playing."""
        pygame.mixer.music.unpause()
        self._playing = True

    def play_loop(self, path: str, loop_instant: int):
        """Play a music that will loop."""
        full_path = get_file('musics', path)
        self._loop_instant = loop_instant
        self._loops_or_playlist = _LOOPS
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play(0)
        self._playing = True
        self._playlist_idx = 0
    
    def read_playlist(self, playlist: list[str], random: bool = False):
        """Play a playlist"""
        self._loops_or_playlist = _PLAYLIST
        self._playlist_idx = 0
        if random:
            shuffle(playlist)
        self._playlist_playing = [get_file('musics', path) for path in playlist]
        self._playing = True
    
    def add_to_playlist(self, path: str):
        """Add a music to the playlist."""
        full_path = get_file('musics', path)
        self._playlist_playing.append(full_path)

    def update(self):
        """This function should be called at the end of every gameloop to make the music loop or the jukebox play a new music."""
        pygame.mixer.music.set_volume(self._settings.volumes['main']*self._settings.volumes['music'])
        # If we are playing a looping music.
        if self._playing and self._loops_or_playlist == _LOOPS and not pygame.mixer.music.get_busy() and self._loop_instant is not None:
            pygame.mixer.music.play(0, self._loop_instant/1000)

        # If we are reading a playlist
        if self._playing and self._loops_or_playlist == _PLAYLIST and not pygame.mixer.music.get_busy():
            self._playlist_idx = (self._playlist_idx+1)%len(self._playlist_playing)
            path = self._playlist_playing[self._playlist_idx]
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(0)
