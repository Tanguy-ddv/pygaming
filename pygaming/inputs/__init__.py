"""The input module contains the Inputs, Controls and Click classes to interact with the user."""
from .inputs import Inputs
from .mouse import Mouse, Click
from .keyboard import Controls, Keyboard
__all__ = ["Click", "Controls", "Inputs", "Mouse", "Keyboard"]
