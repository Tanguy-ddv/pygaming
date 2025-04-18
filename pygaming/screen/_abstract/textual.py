from .child import Child
from .master import Master
from ...color import Color
from ...database import TextFormatter

class Textual(Child):
    
    def __init__(self, master: Master, update_if_invisible, font: str, color: Color, text_or_loc: str, justify: TextFormatter) -> None:
        super().__init__(master, update_if_invisible)
        self._font = font
        self._color = color
        self.text = text_or_loc
        self.justify = justify

    def set_text_or_loc(self, new_text_or_loc: str | TextFormatter):
        """Reset the text or loc to a new value."""
        self._text = new_text_or_loc
        self.notify_change()
