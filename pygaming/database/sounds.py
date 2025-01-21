"""The Sound class is used to store sounds, the SoundBox class is used to manage them."""

from ..settings import Settings
from pygame.mixer import Sound as _Sd
from ..error import PygamingException
from ..file import get_file
from .database import Database
from .speeches import Speeches

class Sound(_Sd):
    """
    A Sound represent a sound stored in the assets/sounds folder.
    The category of the sound
    """

    def __init__(self, path: str, category) -> None:
        super().__init__(get_file('sounds', path))
        self.category = category

class SoundBox:
    """The Sound box is used to play all the sounds."""

    def __init__(self, settings: Settings, first_phase: str, database: Database) -> None:
        self._phase_name = first_phase
        self._db = database
        self._speeches = Speeches(database, settings, first_phase)
        this_phase_speech_paths, all_phases_speech_paths =  self._speeches.get_all()

        self._this_phase_paths: dict[str, (str, str)] = {loc : (path, "speeches") for loc, path in this_phase_speech_paths.items()}
        self._this_phase_paths.update(database.get_sounds(first_phase))

        self._all_phases_paths: dict[str, (str, str)] = {loc : (path, "speeches") for loc, path in all_phases_speech_paths.items()}
        self._all_phases_paths.update(database.get_sounds('all'))

        self._sounds = self._get_sounds_dict()

    def _get_sounds_dict(self) -> dict[str, Sound]:
        """Create the full dict of sounds."""
        dall = {name : Sound(path, category) for name, (path, category) in self._this_phase_paths.items()}
        dthis = {name : Sound(path, category) for name, (path, category) in self._all_phases_paths.items()}
        return {**dall, **dthis}

    def update_settings(self, settings: Settings, phase: str):
        """Change the speeches based on the language and the volumes based on the new volumes."""
        last_language = self._speeches.current_language
        last_phase = self._speeches.current_phase
        self._speeches.update(settings, phase)
        this_phase_speech_paths, all_phases_speech_paths =  self._speeches.get_all()
        if last_phase != phase:
            self._this_phase_paths: dict[str, (str, str)] = {loc : (path, "speeches") for loc, path in this_phase_speech_paths.items()}
            self._this_phase_paths.update(self._db.get_sounds(phase))

        if last_language != settings.language: # if the language change, we reload all speeches
            if last_phase == phase: # If the phase changed as well, we already update the speeches based on new phase and language above
                self._this_phase_paths.update({loc : (path, "speeches") for loc, path in this_phase_speech_paths.items()})
            self._all_phases_paths.update({loc : (path, "speeches") for loc, path in all_phases_speech_paths.items()})

        self._sounds = self._get_sounds_dict()

        # Verify all categories exists and set the sound.
        for sound in self._sounds.values():
            if sound.category not in settings.volumes["sounds"]:
                raise PygamingException(f"The sound category {sound.category} is not listed in the settings, got\n {list(settings.volumes['sounds'].keys())}.")
            sound.set_volume(settings.volumes["sounds"][sound.category]*settings.volumes["main"])

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
        sd = self._sounds.get(name_or_loc, None)
        if sd is None:
            raise PygamingException(f"The name {name_or_loc} is neither a sound nor a localization of the phase {self._phase_name}. The sounds loaded are:\n{self.get_sounds_names}")

        sd.play(loop, maxtime_ms, fade_ms)

    def get_sounds_names(self):
        """Return the list of the name of the sounds loaded for the phase."""
        return list(self._sounds.keys())
