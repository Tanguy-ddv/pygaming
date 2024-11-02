"""The Sound class is used to store sounds, the SoundBox class is used to manage them."""

from ..settings import Settings
from pygame.mixer import Sound as Sd
from ..error import PygamingException
from ..file.file import get_file
from .database import Database
from .speeches import Speeches

class Sound(Sd):
    """
    A Sound represent a sound stored in the assets/sounds folder.
    The category of the sound
    """

    def __init__(self, path: str, category) -> None:
        self._full_path = get_file('sounds', path)
        super().__init__(self._full_path)
        self.category = category

class SoundBox:
    """The Sound box is used to play all the sounds."""

    def __init__(self, settings: Settings, phase_name: str, database: Database) -> None:
        self._settings = settings
        self._phase_name = phase_name
        self._db = database
        self._speeches = Speeches(database, settings, phase_name)
        speech_paths =  self._speeches.get_all()
        self._paths: dict[str, (str, str)] = {loc : (path, "speeches") for loc, path in speech_paths.items()}
        self._paths.update(database.get_sounds(phase_name))
        self._sounds = {name : Sound(path, category) for name, (path, category) in self._paths.items()}
        self.update_settings()
    
    def update_settings(self):
        """Change the speeches based on the language and the volumes based on the new volumes."""
        if self._speeches.language != self._settings.language:
            self._speeches = Speeches(self._db, self._settings, self._phase_name)
            speech_paths =  self._speeches.get_all()
            self._paths.update({loc : (path, "speeches") for loc, path in speech_paths.items()})
            self._sounds = {name : Sound(path) for name, path in self._paths.items()}
        
        for sound in self._sounds.values():
            if sound.category not in self._settings.volumes["sounds"]:
                raise PygamingException(f"The sound category {sound.category} is not listed in the settings, got\n {list(self._settings.volumes['sounds'].keys())}.")
            sound.set_volume(self._settings.volumes["sounds"][sound.category]*self._settings.volumes["main"])        

    def play_sound(self, name_or_loc: str, loop: int = 0, maxtime_ms: int = 0, fade_ms: int = 0):
        """
        Play the sound with the proper volume.
        
        Params:
        --------
        - name_or_loc: str, the name of the sound or the loc of the speech as reported in the database.
        - loop: int, the number of times the sound will be repeated, default is 0
        - maxtime_ms: int, the maximum time (in ms) the sound can last. If 0, the sound will be played until its end.
        - fade_ms: int, the duration of the fade up (in ms). The sound will start at volume 0 and reach its full volume at fade_ms.
        """
        try:
            sd = self._sounds[name_or_loc]
        except KeyError:
            raise PygamingException(f"The name {name_or_loc} is neither a sound nor a localization of the phase {self._phase_name}. The sounds loaded are:\n{self.get_sounds_names}")

        sd.play(loop, maxtime_ms, fade_ms)
    
    def get_sounds_names(self):
        """Return the list of the name of the sounds loaded for the phase."""
        return list(self._sounds.keys())
