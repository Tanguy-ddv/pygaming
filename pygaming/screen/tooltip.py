"""the element module contains the Element object, which is a base for every object displayed on the game window."""
import pygame
from ..phase import GamePhase
from .art.art import Art

class Tooltip():
    """Element is the abstract class for everything object displayed on the game window: widgets, actors, decors, frames."""

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
        frame is hovered by the mouse.
        """

        self.background = background
        self.children = []

        self.width, self.height = self.background.width, self.background.height
        self.phase = phase

        self._last_surface: pygame.Surface = None
        self._surface_changed: bool = True

        self._rect = pygame.Rect(0, 0, self.width, self.height)

        self.absolute_left, self.absolute_top = 0, 0 # use by children, just an artefact.
    
    @property
    def game(self):
        """Return the game."""
        return self.phase.game

    def is_child_on_me(self, child):
        """Return whether the child is visible on the frame or not."""
        return self._rect.colliderect(child.relative_rect)

    @property
    def visible_children(self):
        """Return the list of visible children sorted by increasing layer."""
        return sorted(filter(lambda ch: ch.visible and ch.on_master, self.children), key= lambda w: w.layer)

    def get_surface(self) -> pygame.Surface:
        """Return the surface to be displayed."""
        if self._surface_changed:
            self._surface_changed = False
            self._last_surface = self.make_surface()
        return self._last_surface

    def make_surface(self) -> pygame.Surface:
        """c the surface of the tooltip as a pygame.Surface"""
        background = self.background.get(self.phase.settings)
        for child in self.visible_children:
            background.blit(child.get_surface(), child.relative_rect.topleft)
        return background

    def is_visible(self):
        """Return True if the tooltip is visible."""
        # Return always True as this is called only when the tooltip is visible
        return True

    def add_child(self, elements):
        """Add a new frame to the phase."""
        self.children.append(elements)

    def loop(self, loop_duration: int):
        """Update the element every loop iteration."""
        has_changed = self.background.update(loop_duration)
        if has_changed:
            self.notify_change()
        for child in self.children:
            child.loop(loop_duration)
    
    def notify_change(self):
        """Called by a children if it changes."""
        self._surface_changed = True

    def begin(self):
        """
        Execute this method at the beginning of the phase
        to load the active area and the surface before running class-specific start method.
        """
        self.background.start(self.phase.settings)
        self.notify_change()
        for child in self.children:
            child.begin()

    def finish(self):
        """Execute this method at the end of the phase, unload the main art and the active area. Call the class-specific end method."""
        self.background.unload()
        for child in self.children:
            child.finish()
