from .base_widget import BaseWidget
import pygame

class MultiStateButton(BaseWidget, MultipleBackGroundsSupport, MouseInteractionSupport, FocusSupport, DisableSupport):
    """A MultiStateButton is a button that switch change when it is clicked."""

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        backgrounds: list[pygame.Color | pygame.Surface],
        focus_backgrounds: list[pygame.Color | pygame.Surface] = None,
        disable_backgrounds: list[pygame.Color | pygame.Surface] = None,
        layer: int = 0,
        initial_value: int = 0,
        hover_cursor: pygame.Cursor = None
    ) -> None:
        BaseWidget.__init__(self, frame, x, y, layer)
        MultipleBackGroundsSupport.__init__(self, backgrounds, initial_value)
        MouseInteractionSupport.__init__(self, self._backgrounds[0], x, y, layer, hover_cursor)