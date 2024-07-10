"""The Sound class is used to store sounds, the SoundBox class is used to manage them."""

from ...io_.file.sound import SoundFile
from ...io_.utils import get_file
import json

SETTINGS_PATH = 'settings.json'

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

        with open(get_file('data', SETTINGS_PATH, dynamic=True)) as f:
            self.volumes = json.load(f)['volume']['sounds']
            self.main_volume = json.load(f)['volume']['main']
        self.categories = list(self.volumes.keys())
    
    def set_sound_volumes(self, sounds_dict: dict) -> None:
        """Set the volume of all the sounds."""
        with open(get_file('data', SETTINGS_PATH, dynamic=True)) as f:
            data = json.load(f)
            current_volumes = data['volume']['sounds']
            if sorted(sounds_dict.keys()) == sorted(current_volumes.keys()):
                data['volume']['sounds'] = sounds_dict
            else:
                raise ValueError("The categories do not correspond.")
        with open(get_file('data', SETTINGS_PATH, dynamic=True), 'w') as f:
            json.dump(data, f)
        self.volumes = sounds_dict
    
    def set_main_volume(self, main_volume):
        """Set the main volume."""
        self.main_volume = main_volume
        with open(get_file('data', SETTINGS_PATH, dynamic=True)) as f:
            data = json.load(f)
            data['volume']['main'] = main_volume
        with open(get_file('data', SETTINGS_PATH, dynamic=True), 'w') as f:
            json.dump(data, f)
    
    def play_sound(self, sound: Sound):
        """Play the sound with the proper volume."""
        sound.set_volume(self.volumes[sound.category]*self.main_volume)
        sound.play()
