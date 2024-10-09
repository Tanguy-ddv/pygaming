"""The label module contains the Label Element used to display text."""
import pygame
from .element import Element, SurfaceLike, TOP_LEFT
from ..font import Font

TEXT_LEFT = 'text_left'
TEXT_RIGHT = 'text_right'
TEXT_CENTERED = 'text_centered'

class Label(Element):
    """A Label is an element used to display text."""

    def __init__(
        self,
        master,
        background: SurfaceLike,
        font: Font,
        localization_or_text: str,
        x: int,
        y: int,
        anchor = TOP_LEFT,
        layer: int = 0,
        justify = TEXT_CENTERED,
        blinking_period: int = None
    ) -> None:
        """
        Create the label
        Params:
        - master: Frame. The Frame in which the Label is placed.
        - background: A SurfaceLike object beiing the background of the text.
        - font: Font, the font to be used to display the text.
        - text: The text to be displayed, can be modify with set_text(new_text).
        - x: The first coordinate of the anchor in the Frame.
        - y: The first coordinate of the anchor in the Frame.
        - anchor: The anchor of the coordinate.
        - layer: int, the layer of the element in the frame.
        - justify: the position of the text in the label. can be TEXT_CENTERED, TEXT_RIGHT, TEXT_LEFT
        - blinking_period: int [ms]. If an integer is specified, the text will blink with the given period.
        """
        self.font = font
        self.text = str(localization_or_text)
        super().__init__(master, background, x, y, anchor, layer, None, None, False, False)
        self.justify = justify
        self._bg_width, self._bg_height = self.surface.width, self.surface.height
        self._blinking_period = blinking_period
        self._time_since_last_blink = 0
        self._show_text = True

    def set_localization_or_text(self, localization_or_text: str):
        """Set the label text to a new value."""
        self.text = str(localization_or_text)

    def update(self, loop_duration: int):
        """Update the blinking of the text."""
        if self._blinking_period is not None:
            self._time_since_last_blink += loop_duration
            if self._time_since_last_blink > self._blinking_period//2:
                self._show_text = not self._show_text
                self._time_since_last_blink = 0

    def get_surface(self) -> pygame.Surface:
        """Return the surface of the Label."""
        bg = self.surface.get()
        if self._show_text:
            rendered_text = self.font.render(self.game.texts.get(self.text))
            text_width, text_height = rendered_text.get_size()
            y = (self._bg_height - text_height)//2
            if self.justify == TEXT_CENTERED:
                x = (self._bg_width - text_width)//2
            elif self.justify == TEXT_RIGHT:
                x = self._bg_width - text_width
            else:
                x = 0
            bg.blit(rendered_text, (x,y))
        return bg
