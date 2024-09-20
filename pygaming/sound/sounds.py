"""The Sound class is used to store sounds, the SoundBox class is used to manage them."""

from ..file import SoundFile
from ..settings import Settings

class Sound:
    """The Sound class represent a sound, it load the category and the file from a SoundFile object."""

    def __init__(self, sound_file: SoundFile) -> None:
        self._sound, self.category = sound_file.get()

    def set_volume(self, volume):
        """Set the volume of the osund"""
        self._sound.set_volume(volume)

    def play(self, loop: int = 0, maxtime: int = 0, fade_ms: int = 0):
        """Play the sound once."""
        self._sound.play(loop, maxtime, fade_ms)

class SoundBox:
    """The Sound box is used to play all the sounds."""

    def __init__(self, settings: Settings) -> None:

        self._settings = settings

    def play_sound(self, sound: Sound, loop: int = 0, maxtime: int = 0, fade_ms: int = 0):
        """Play the sound with the proper volume."""
        sound.set_volume(self._settings.volumes["sounds"][sound.category]*self._settings.volumes["main"])
        sound.play(loop, maxtime, fade_ms)
