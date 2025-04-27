"""the element module contains the Element object, which is a base for every object displayed on the game window."""
import pygame
from ...settings import Settings
from ..art.art import Art
from ...database import TextFormatter
from ...color import ColorLike
from ..anchors import CENTER_CENTER, AnchorLike, Anchor
from .._abstract import Graphical, Textual

class Tooltip(Graphical):
    """Tooltip is a graphical overlay displayed on hover."""

    def __init__(
        self,
        background: Art,
        **kwargs,
    ) -> None:
        """
        Create a Tooltip.

        Params:
        ----
        - background: Art, The image to be displayed
        """
        super().__init__(background, **kwargs)
    
    def get_surface(self, phase) -> pygame.Surface:
        """Return the surface to be displayed."""
        if self._surface_changed or self._last_surface is None:
            self._surface_changed = False
            self._last_surface = self.make_surface(phase)
        return self._last_surface

    def make_surface(self, phase) -> pygame.Surface:
        """Create the image of the visual as a pygame surface."""
        return self._arts.get(**phase.settings)

class TextTooltip(Tooltip, Textual):
    """A TextTooltip is a tooltip with some text displayed on it."""

    def __init__(self, background, text_or_loc: str | TextFormatter, font: str, font_color: ColorLike, jusitfy: AnchorLike = CENTER_CENTER, **kwargs):
        super().__init__(background=background, font=font, color=font_color, jusitfy=jusitfy, text_or_loc=text_or_loc, **kwargs)

    def make_surface(self, phase):
        """Make the surface of the tooltip with the text on it."""
        return self._render_text_on_bg(phase.settings, phase.typewriter)
