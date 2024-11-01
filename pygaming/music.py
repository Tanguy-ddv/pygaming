"""The Jukebox class is used to manage the musics."""

from random import random as rd
import pygame
from .file import MusicFile
from .settings import Settings

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

    def play_loop(self, music_file: MusicFile):
        """Play a music that will loop."""
        path, self._loop_instant = music_file.get()
        self._loops_or_playlist = _LOOPS
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(0)
        self._playing = True
        self._playlist_idx = 0
    
    def read_playlist(self, playlist: list[MusicFile], random: bool = False):
        """Play a playlist"""
        self._loops_or_playlist = _PLAYLIST
        self._playlist_idx = 0
        if random:
            playlist = sorted(playlist, key= lambda music: rd())
        self._playlist_playing = playlist
        self._playing = True
    
    def add_to_playlist(self, music_file: MusicFile):
        """Add a music to the playlist."""
        self._playlist_playing.append(music_file)

    def update(self):
        """This function should be called at the end of every gameloop to make the music loop or the jukebox play a new music."""
        pygame.mixer.music.set_volume(self._settings.volumes['main']*self._settings.volumes['music'])
        # If we are playing a looping music.
        if self._loops_or_playlist == _LOOPS and not pygame.mixer.music.get_busy() and self._playing and self._loop_instant is not None:
            pygame.mixer.music.play(0, self._loop_instant/1000)

        # If we are reading a playlist
        if self._loops_or_playlist == _PLAYLIST and not pygame.mixer.music.get_busy() and self._playing:
            self._playlist_idx = (self._playlist_idx+1)%len(self._playlist_playing)
            path, _ = self._playlist_playing[self._playlist_idx].get()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(0)
