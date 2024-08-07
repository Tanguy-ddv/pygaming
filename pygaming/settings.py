"""The settings class is used to interact with the settings file."""
from .file import get_file
import json
from typing import Any
from .error import PygamingException

class Settings:
    """The settings class is used to interact with the settings file."""

    def __init__(self, jukebox, soundbox, controls, texts, screen, ) -> None:
        self._path = get_file('data', 'settings.json', False)
        file = open(self._path, 'r', encoding='utf-8')
        self._data = json.load(file)
        file.close()
        self._jukebox = jukebox # Link the jukebox to give it directly the volumes
        self._jukebox.update_settings(self)
        self._soundbox = soundbox # Link the soundbox to give it directly the volumes
        self._soundbox.update_settings(self)
        self._controls = controls # Link the controls to give it directly the key mapping
        self._controls.update_settings(self)
        if texts is not None:
            self._texts = texts # Link the texts to give the current language.
            self._texts.update_settings(self)
        else:
            self._texts = None
        self._screen = screen
        self._screen.update_settings(self)

    def get(self, attribute: str):
        """Get the value of the settings attribute"""
        if attribute in self._data:
            return self._data[attribute]
        return None
    
    @property
    def language(self) -> str:
        return self._data['current_language']
    
    @property
    def fullscreen(self) -> bool:
        return self._data['full_screen']
    
    @property
    def controls(self) -> dict[str, str]:
        return self._data['controls']
    
    @property
    def volumes(self) -> dict[str, Any]:
        return self._data['volumes']

    def set_volumes(self, volumes: dict[str, Any]):
        """
        Set the volumes to new values.
        The new volumes must be a dict with keys: 'main', 'sounds' and 'music',
        with 'main' and 'music' mapping to a number between 0 and 1
        and 'sounds' mapping to a dict of category : number between 0 and 1.
        The categories of the new volumes and the previous volume must be the exact same.
        """
        if not ('main' in volumes and 'sounds' in volumes and 'music' in volumes):
            raise PygamingException("'main', 'sounds' or 'music' is not present in the new volumes dict.")
        for key in self._data['volumes']['sounds']:
            if key not in volumes['sounds']:
                raise PygamingException(f"The category {key} is not present in the new sounds volumes.")
        for key in volumes['sounds']:
            if key not in self._data['volumes']['sounds']:
                raise PygamingException(f"The category {key} is not defined in the settings files.")
        self._data['volumes'] = volumes
        self._jukebox.update_settings(self)
        self._soundbox.update_settings(self)

    def set_language(self, language: str):
        """Set the new language."""
        self._data['current_language'] = language
        if self._texts is not None:
            self._texts.update_settings(self)
        
    def set_controls(self, controls: dict[str, str]):
        """Set the new keymap."""
        for key in self.controls.values():
            if key not in controls.values():
                raise PygamingException(f"the action {key} have not been mapped.")
        for key in controls.values():
            if key not in self.controls.values():
                raise PygamingException(f"the action {key} does not exists.")
        self._data['controls'] = controls
        self._controls.update_settings(self)
    
    def set_full_screen(self, full_screen : bool):
        """Set the full screen."""
        self._data['full_screen'] = full_screen
        self._screen.update_settings(self)

    def set_attribute(self, attribute: str, value: Any):
        """Set the new value for a given attribute."""
        if attribute not in self._data:
            raise PygamingException(f"{attribute} is not an attribute of the settings.")
        if attribute in ['volumes', 'current_language', 'full_screen', 'controls']:
            raise PygamingException(f"Please set {attribute} with it dedecated setter.")
        self._data[attribute] = value

    def __del__(self):
        """Delete the object at the end of the game."""
        file = open(self._path, 'r', encoding='utf-8')
        json.dump(self._data, file)
        file.close()
        del self
    
