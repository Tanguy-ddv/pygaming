"""The label module contains the Label Element used to display text."""
import pygame
from ..element import Element
from ..anchors import TOP_LEFT, CENTER
from ...color import Color
from ..art.art import Art
from ...database import TextFormatter


class Label(Element):
    """A Label is an element used to display text."""

    def __init__(
        self,
        master,
        background: Art,
        font: str,
        font_color: Color,
        localization_or_text: str | TextFormatter,
        x: int,
        y: int,
        anchor = TOP_LEFT,
        layer: int = 0,
        justify = CENTER,
        blinking_period: int = None
    ) -> None:
        """
        Create the label
        Params:
        - master: Frame. The Frame in which the Label is placed.
        - background: A SurfaceLike object beiing the background of the text.
        - font: Font, the font to be used to display the text.
        - localization_or_text: The text, localization or TextFormatter to be displayed, can be modify with set_localization_or_text(new_text).
        - x: The first coordinate of the anchor in the Frame.
        - y: The first coordinate of the anchor in the Frame.
        - anchor: The anchor of the coordinate.
        - layer: int, the layer of the element in the frame.
        - justify: the position of the text in the label, should be an anchor (i.e a tuple[x, y] with 0 <= x, y <= 1, )
        - blinking_period: int [ms]. If an integer is specified, the text will blink with the given period.
        """
        self.font = font
        self.text = str(localization_or_text)
        super().__init__(master, background, x, y, anchor, layer, None, None, False, False, None)
        self.justify = justify
        self._bg_width, self._bg_height = self.surface.width, self.surface.height
        self._blinking_period = blinking_period
        self._time_since_last_blink = 0
        self._show_text = True
        self.font_color = font_color

    def set_localization_or_text(self, localization_or_text: str):
        """Set the label text to a new value."""
        if not isinstance(localization_or_text, (str, TextFormatter)):
            self.master.game.logger.write({"LabelError" : str(localization_or_text)}, True)
            localization_or_text = str(localization_or_text)
        elif self.text != localization_or_text:
            self.text = localization_or_text
            self.notify_change()

    def update(self, loop_duration: int):
        """Update the blinking of the text."""
        if self._blinking_period is not None:
            self._time_since_last_blink += loop_duration
            if self._time_since_last_blink > self._blinking_period//2:
                self._show_text = not self._show_text
                self._time_since_last_blink = 0
                self.notify_change()

    def make_surface(self) -> pygame.Surface:
        """Return the surface of the Label."""
        bg = self.surface.get(self.game.settings)
        if self._show_text:
            rendered_text = self.game.typewriter.render(self.font, self.text, self.font_color, None, self.justify)
            text_width, text_height = rendered_text.get_size()
            just_x = self.justify[0]*(self.surface.width - text_width)
            just_y = self.justify[1]*(self.surface.height - text_height)
            bg.blit(rendered_text, (just_x, just_y))
        return bg
    
    def start(self):
        """Nothing to do at start."""
        pass

    def end(self):
        """Nothing to do at the end."""
        pass
