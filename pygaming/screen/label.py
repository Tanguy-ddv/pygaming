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
        text: str,
        x: int,
        y: int,
        anchor = TOP_LEFT,
        layer: int = 0,
        text_anchor = TEXT_CENTERED
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
        """
        self.font = font
        self.text = str(text)
        super().__init__(master, background, x, y, anchor, layer, None, None, False, False)
        self.text_anchor = text_anchor
        self._bg_width, self._bg_height = self.surface.width, self.surface.height

    def set_text(self, text: str):
        """Set the label text to a new value."""
        self.text = str(text)

    def update(self, loop_duration: int):
        pass

    def get_surface(self) -> pygame.Surface:
        """Return the surface of the Label."""
        bg = self.surface.get()
        rendered_text = self.font.render(self.text)
        text_width, text_height = rendered_text.get_size()
        y = (self._bg_height - text_height)//2
        if self.text_anchor == TEXT_CENTERED:
            x = (self._bg_width - text_width)//2
        elif self.text_anchor == TEXT_RIGHT:
            x = self._bg_width - text_width
        else:
            x = 0
        bg.blit(rendered_text, (x,y))
        return bg
