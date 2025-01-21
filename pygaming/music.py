"""The Jukebox class is used to manage the musics."""

from random import shuffle
from typing import Union
import os
import pygame
from .settings import Settings
from .file import get_file

_LOOPS = 'loops'
_PLAYLIST = 'playlist'

class Jukebox:
    """The Jukebox is used to manage the musics."""

    def __init__(self, settings: Settings) -> None:

        self._introduction = 0
        self._playing = False
        self._loops_or_playlist = _LOOPS
        self._playlist_idx = 0
        self._playlist = []
        self.update_settings(settings)

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

    def play_loop(self, path: str, introduction: int = 0):
        """
        Play a music that will loop.
        
        Params:
        ----
        - path: str, the path to the music file in the assets/musics/ folder
        - introduction: int (ms), the duration of the introduction of the music. 

        Example:
        -----

        >>> jukebox.play_loop("my_music.mp3", 5000)
        will play assets/musics/my_music.mp3. Once the music is over, resume the play at the instant 5000 ms
        """
        full_path = get_file('musics', path)
        self._introduction = introduction
        self._loops_or_playlist = _LOOPS
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play(0)
        self._playing = True
        self._playlist_idx = 0

    def read_playlist(self, playlist: Union[str,list[str]], random: bool = False):
        """
        Play a playlist.

        Params:
        -----
        - playlist: str, list[str]. A folder or a list of file in the assets/musics folder
        - random: bool, if True, randomize the playlist to be played
        
        Examples:
        -----
        >>> jukebox.read_playlist('my_playlist/', '')
        """

        self._loops_or_playlist = _PLAYLIST
        self._playlist_idx = 0
        if isinstance(playlist, str):
            # We have a folder
            folder = get_file('musics', playlist)
            self._playlist = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        else:
            # We have a list of paths
            self._playlist = [get_file('musics', path) for path in playlist]
        if random:
            shuffle(self._playlist)
        self._playing = True

    def add_to_playlist(self, path: str):
        """Add a music to the playlist."""
        full_path = get_file('musics', path)
        self._playlist.append(full_path)

    def update(self):
        """This function should be called at the end of every gameloop to make the music loop or the jukebox play a new music."""

        # If we are playing a looping music.
        if self._playing and self._loops_or_playlist == _LOOPS and not pygame.mixer.music.get_busy() and self._loop_instant is not None:
            pygame.mixer.music.play(0, self._loop_instant/1000)

        # If we are reading a playlist
        if self._playing and self._loops_or_playlist == _PLAYLIST and not pygame.mixer.music.get_busy():
            self._playlist_idx = (self._playlist_idx+1)%len(self._playlist)
            path = self._playlist[self._playlist_idx]
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(0)

    def update_settings(self, settings: Settings):
        """Update the current settings of the jukebox."""
        pygame.mixer.music.set_volume(settings.volumes['main']*settings.volumes['music'])
