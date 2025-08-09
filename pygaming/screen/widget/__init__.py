"""Pygaming widgets are used to interact with the player."""
from .button import Button, TextButton, MultiStateButton, TextMultiStateButton
from .entry import Entry, Text
from .label import Label, Paragraph
from .slider import Slider, TextSlider, MultiAspectSlider
from .progress_bar import ProgressBar, TextProgressBar
from .canvas import Canvas
from .figure import Figure
from .view import View
from .scrollbar import HScrollBar, VScrollBar
from .spinbox import SpinBox
from .checkbox import CheckBox, RadioButtons

__all__ = ['Button', 'TextButton', 'Entry', 'Label', 'Slider', 'Paragraph', 'View', 'MultiStateButton', 'TextMultiStateButton',
           'SpinBox', 'RadioButtons', 'ProgressBar', 'TextProgressBar', 'TextSlider',
           'Text', 'Canvas', 'Figure', 'HScrollBar', 'VScrollBar', 'MultiAspectSlider', 'CheckBox']
