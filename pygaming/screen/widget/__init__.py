"""Pygaming widgets are used to interact with the player."""
from .button import Button, TextButton
from .entry import Entry, Text
from .label import Label, Paragraph
from .slider import Slider, TextSlider
from .widget import Widget
from .progress_bar import ProgressBar, TextProgressBar
from .canvas import Canvas

__all__ = ['Button', 'TextButton', 'Entry', 'Label', 'Slider', 'Widget', 'Paragraph',
           'ProgressBar', 'TextProgressBar', 'TextSlider', 'Text', 'Canvas']
