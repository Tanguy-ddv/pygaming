"""the element module contains the Element object, which is a base for every object displayed on the game window."""
import pygame
from ..phase import GamePhase
from .art.art import Art
from ..database import TextFormatter
from ..color import ColorLike
from .anchors import CENTER
from ._abstract import Visual

class Tooltip(Visual):
    """Tooltip is a graphical overlay displayed on hover."""

    def __init__(
        self,
        phase: GamePhase,
        background: Art,        
    ) -> None:
        """
        Create an Element.

        Params:
        ----
        - phase: Frame or Phase, the master of this object.
        - background: The surface. It is an Art
        """

        self.phase = phase
        Visual.__init__(self, background, False)

    @property
    def game(self):
        """Return the game."""
        return self.phase.game


    def make_surface(self) -> pygame.Surface:
        """Make the surface of the tooltip as a pygame.Surface"""
        return self.background.get(self.phase.settings)

    def loop(self, loop_duration: int):
        """Update the element every loop iteration."""
        has_changed = self.background.update(loop_duration)
        if has_changed:
            self.notify_change()
    
    def notify_change(self):
        """Called by a children if it changes."""
        self._surface_changed = True

    def begin(self):
        """Execute this method at the beginning of the phase"""
        self.background.start(self.phase.settings)
        self.notify_change()

    def finish(self):
        """Execute this method at the end of the phase, unload the main art and the active area. Call the class-specific end method."""
        self.background.unload()

class TextTooltip(Tooltip):

    def __init__(self, phase, background, text_or_loc: str | TextFormatter, font: str, font_color: ColorLike, jusitfy: tuple[float, float] = CENTER):
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
        background = self.background.get(self.phase.settings)
        rendered_text = self.game.typewriter.render(self._font, self._text, self._font_color, None, self._justify)
        text_width, text_height = rendered_text.get_size()
        just_x = self._justify[0]*(background.get_width() - text_width)
        just_y = self._justify[1]*(background.get_height() - text_height)
        background.blit(rendered_text, (just_x, just_y))
        return background
