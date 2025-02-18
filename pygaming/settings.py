"""The settings class is used to interact with the settings file."""
from typing import Any
from .file import load_json_file, save_json_file
from .error import PygamingException
from .config import Config

class Settings:
    """
    The settings class is used to interact with the settings file.
    Every game setting is stored here: controls, language, full screen etc.
    You can also store your own settings by modify the data/settings.json files
    to add your own controls and settings.
    For instance, difficulty, rendering etc.
    """

    def __init__(self, config: Config) -> None:
        self._data, self._encoding = load_json_file('settings.json')
        self._ld_kwargs_keys = config.get("loading_kwargs", ["antilias", "cost_threshold"])

    def get(self, attribute: str):
        """Get the value of the settings attribute"""
        if attribute in self._data:
            return self._data[attribute]
        return None

    @property
    def language(self) -> str:
        """Return the current language setting."""
        return self._data['current_language']

    @property
    def antialias(self) -> bool:
        """Return the antialias setting."""
        if 'antialias' in self._data:
            return self._data['antialias']
        return True

    @property
    def fullscreen(self) -> bool:
        """Return the fullscreen setting."""
        if "fullscreen" in self._data:
            return self._data['fullscreen']
        return False

    @property
    def controls(self) -> dict[str, str]:
        """Return the controls."""
        return self._data['controls']

    @property
    def volumes(self) -> dict[str, Any]:
        """Return the volumes."""
        return self._data['volumes']

    def save(self) -> None:
        """Save the current settings."""
        save_json_file('settings.json', self._data, self._encoding)

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
        self.save()

    def set_language(self, language: str):
        """Set the new language."""
        self._data['current_language'] = language
        self.save()

    def set_controls(self, controls: dict[str, str], phase: str):
        """Set the new keymap."""
        for key in self.controls[phase].values():
            if key not in controls.values():
                raise PygamingException(f"the action {key} have not been mapped.")
        for key in controls.values():
            if key not in self.controls[phase].values():
                raise PygamingException(f"the action {key} does not exists.")
        self._data['controls'][phase] = controls
        self.save()

    def set_fullscreen(self, fullscreen : bool):
        """Set the full screen."""
        self._data['fullscreen'] = fullscreen
        self.save()

    def set_attribute(self, attribute: str, value: Any):
        """Set the new value for a given attribute."""
        if attribute not in self._data:
            raise PygamingException(f"{attribute} is not an attribute of the settings.")
        if attribute in ['volumes', 'current_language', 'full_screen', 'controls']:
            raise PygamingException(f"Please set {attribute} with it dedecated setter.")
        self._data[attribute] = value
        self.save()
    
    def keys(self):
        """This method is used to return the name of the loading kwargs for arts and masks."""
        return self._ld_kwargs_keys

    def __getitem__(self, name):
        return self._data.get(name)
