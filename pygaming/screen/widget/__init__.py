"""Pygaming widgets are used to interact with the player."""
from .button import Button, TextButton, MultiStateButton, TextMultiStateButton
from .entry import Entry, Text
from .label import Label, Paragraph
from .slider import Slider, TextSlider
from .widget import Widget, TextualWidget
from .progress_bar import ProgressBar, TextProgressBar
from .canvas import Canvas
from .figure import Figure
from .view import View
from .scrollbar import HScrollBar, VScrollBar

__all__ = ['Button', 'TextButton', 'Entry', 'Label', 'Slider', 'Widget', 'Paragraph', 'View', 'MultiStateButton', 'TextMultiStateButton',
           'ProgressBar', 'TextProgressBar', 'TextSlider', 'Text', 'Canvas', 'Figure', 'TextualWidget', 'HScrollBar', 'VScrollBar']
