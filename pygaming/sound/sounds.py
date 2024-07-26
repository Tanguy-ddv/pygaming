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
    
    def play(self):
        """Play the sound once."""
        self._sound.play(0)
    
class SoundBox:
    """The Sound box is used to play all the sounds."""

    def __init__(self) -> None:

        self.main_volume = 1
        self.volumes = {'unavailable' : 1}
    
    def update_settings(self, settings: Settings):
        """Update the volumes with the settings."""
        volumes = settings.volumes
        self.main_volume = volumes['main']
        self.volumes = volumes['sounds']
        self.volumes['unavailable'] = 1
    
    def play_sound(self, sound: Sound):
        """Play the sound with the proper volume."""
        sound.set_volume(self.volumes[sound.category]*self.main_volume)
        sound.play()
