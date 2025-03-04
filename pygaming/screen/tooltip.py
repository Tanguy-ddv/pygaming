"""the element module contains the Element object, which is a base for every object displayed on the game window."""
import pygame
from ..phase import GamePhase
from .art.art import Art
from ..database import TextFormatter
from ..color import ColorLike
from .anchors import CENTER, Anchor
from ._visual import Visual

class Tooltip(Visual):
    """Tooltip is a graphical overlay displayed on hover."""

    def __init__(
        self,
        phase: GamePhase,
        background: Art
    ) -> None:
        """
        Create a Tooltip.

        Params:
        ----
        - phase: GamePhase, the master of this object.
        - background: Art, The image to be displayed
        """
        self.phase = phase
        Visual.__init__(self, background, False)

    @property
    def game(self):
        """Return the game."""
        return self.phase.game

    def make_surface(self) -> pygame.Surface:
        """Make the surface of the tooltip as a pygame.Surface"""
        return self.background.get(None, **self.phase.settings)

class TextTooltip(Tooltip):
    """A TextTooltip is a tooltip with some text displayed on it."""

    def __init__(self, phase, background, text_or_loc: str | TextFormatter, font: str, font_color: ColorLike, jusitfy: Anchor = CENTER):
        super().__init__(phase, background)

        self._text = text_or_loc
        self._font = font
        self._font_color = font_color
        self._justify = jusitfy

    def set_text_or_loc(self, new_text_or_loc: str | TextFormatter):
        """Reset the text or loc to a new value."""
        self._text = new_text_or_loc
        self.notify_change()

    def make_surface(self):
        """Make the surface of the tooltip with the text on it."""
        background = self.background.get(None, **self.phase.settings)
        rendered_text = self.game.typewriter.render(self._font, self._text, self._font_color, None, self._justify)
        text_width, text_height = rendered_text.get_size()
        just_x = self._justify[0]*(background.get_width() - text_width)
        just_y = self._justify[1]*(background.get_height() - text_height)
        background.blit(rendered_text, (just_x, just_y))
        return background
