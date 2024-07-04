from abc import ABC, abstractmethod
import pygame
from ..inputs import Inputs
from ...utils.color import Color
from ...utils.text_flags import TextFlags
from ...io_.file import FontFile

class BaseWidget(ABC):

    def __init__(self, frame, x: int, y: int, width: int, height: int, background: pygame.Surface, focus_background: pygame.Surface, initial_focus: bool = False) -> None:
        super().__init__()
        self._focus = initial_focus
        self.frame = frame
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.unfocus_background = pygame.transform.scale(background, (width, height))
        self.focus_background = pygame.transform.scale(focus_background, (width, height))
        self.visible = True
        frame.add_widget(self)

    def focus(self):
        self._focus = True
    
    def unfocus(self):
        self._focus = False
    
    def hide(self):
        self.visible = False
    
    def show(self):
        self.visible = True
    
    @abstractmethod
    def get_surface(self) -> pygame.Surface:
        """Return the surface to be blitted."""
        raise NotImplementedError()

    @abstractmethod
    def update(self, inputs: Inputs, loop_duration: int, x: int, y: int):
        """Update the widget with the inputs."""
        raise NotImplementedError()

    def move(self, new_x, new_y):
        """Move the widget on the frame."""
        self.x = new_x
        self.y = new_y

class BaseWidgetWithText(BaseWidget):
    """A basic widget that might display some text."""

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        width: int,
        height: int,
        background: pygame.Surface,
        focus_background: pygame.Surface,
        font_color: Color,
        flags: TextFlags,
        font_file: FontFile,
        font_size: int,
        initial_focus: bool = False
    ) -> None:
        super().__init__(frame, x, y, width, height, background, focus_background, initial_focus)
        self._font_color = font_color.to_RGBA()
        self._font = FontFile.get(font_file, font_size, flags.italic, flags.bold, flags.underline)
        self._antialias = flags.antialias

    def _render(self, text: str):
        return self._font.render(text, self._antialias, self._font_color)

    