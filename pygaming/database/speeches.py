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

    def __init__(self, database: Database, settings: Settings, first_phase: str) -> None:
        self._db = database
        self._settings = settings
        self.current_language = settings.language
        self._all_phases_dict = self._query_db(self.current_language, 'all')
        self._this_phase_dict = self._query_db(self.current_language, first_phase)
        self.current_phase = first_phase

    def _query_db(self, language, phase_name):
        """Query the database for the speeches"""
        texts_list = self._db.get_speeches(language, phase_name)
        return {pos : txt for pos, txt in texts_list}

    def get_all(self):
        """Return all the locs and speech paths."""
        return self._this_phase_dict, self._all_phases_dict

    def update(self, settings: Settings, phase: str) -> bool:
        """Update the language and/or phase of the speeches"""
        if settings.language == self.current_language:
            if phase != self.current_phase: # Same language, different phase
                self._this_phase_dict = self._query_db(settings.language, phase)
                self.current_phase = phase
        else:
            # Different language
            self._all_phases_dict = self._query_db(settings.language, 'all')
            self._this_phase_dict = self._query_db(settings.language, phase)
            self.current_language = settings.language
