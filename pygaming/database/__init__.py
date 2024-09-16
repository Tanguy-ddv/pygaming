"""
The database module contains the database class to interaxct with the database
the texts and speeches to display texts ad play sounds in the good language.
"""
from .database import Database
from .texts import Texts
from .speeches import Speeches
__all__ = ['Texts', 'Database', 'Speeches']
