"""
The Speeches class is used to manage the speeches of the game by returning SoundFile taking
automatically into account the language, use it with the Soundbox.
"""

from .database import Database
from ..settings import Settings

class Speeches:
    """
    The class Speeches is used to manage the texts of the game, that might be provided in several languages.
    """

    def __init__(self, database: Database, settings: Settings, phase_name: str) -> None:
        self._db = database
        self._settings = settings
        self.language = settings.language
        path_list = self._db.get_speeches(self.language, phase_name)
        self._speeches_dict = {pos : txt for pos, txt in path_list[0]}

    def get_all(self):
        """Return all the locs and speech paths."""
        return self._speeches_dict
