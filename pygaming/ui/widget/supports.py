import pygame
from abc import ABC, abstractmethod
from typing import overload
from ...utils.color import Color
from ...io_.file import FontFile
from ..inputs import Inputs
import numpy as np
from ..positionable import Positionable
from ...io_.utils import get_file
import json
__CONFIG_FILE = get_file('data', 'config.json', dynamic=True)


class TextSupport(ABC):
    """
    Add text support for the widget, use it as parent class alongside BaseWidget for your widgets.
    use ._render(text) to get a surface with the text on it.
    use the different setters to modify the class.
    """

    def __init__(
        self,
        font_color: Color,
        font_file: FontFile,
        font_size: int,
        italic: bool = False,
        bold: bool = False,
        underline: bool = False,
        antialias: bool = True,
    ) -> None:
        """
        Add text support for a widget.
        
        Params:
        ---
        font_color: Color, the color of the text.
        font_file: Fontfile, the font of the text.
        font_size: int, the size of the font.
        italic, bold, underline and alias: bool, flags to specify if the font is bold, italic etc.
        """
        ABC.__init__(self)
        self.__font_color = font_color.to_RGBA()
        self._font = FontFile.get(font_file, font_size, italic, bold, underline)
        self.__antialias = antialias
        self.__bold = bold
        self.__font_file = font_file
        self.__underline = underline
        self.__italic = italic
        self.__font_size = font_size
    
    def __update_font(self):
        self._font = FontFile.get(
            self.__font_file,
            self.__font_size,
            self.__italic,
            self.__bold,
            self.__underline
        )

    def _render(self, text: str) -> pygame.Surface:
        return self._font.render(text, self.__antialias, self.__font_color)

    def set_bold(self, bold: bool):
        """Set the bold flag."""
        self.__bold = bold
        self.__update_font()
    
    def set_italic(self, italic: bool):
        """Set the italic flag."""
        self.__italic = italic
        self.__update_font()
    
    def set_antialias(self, antialias: bool):
        """Set the antialis flag."""
        self.__antialias = antialias
        self.__update_font()
    
    def set_underline(self, underline: bool):
        """Set the underline flag."""
        self.__underline = underline
        self.__update_font()
    
    def set_font_size(self, font_size: bool):
        """Set the font size."""
        self.__font_size = font_size
        self.__update_font()
    
    def set_font(self, font_file: FontFile):
        """Set the font."""
        self.__font_file = font_file
        self.__update_font()
    
    def set_color(self, font_color: Color):
        """Set the color."""
        self.__font_color = font_color.to_RGBA()
        self.__update_font()

class BackgroundSupport(ABC):
    """
    Add a background to the widget.
    """

    def __init__(self, background: pygame.Surface) -> None:
        ABC.__init__(self)
        self._background = background.copy()
    
    @property
    def height(self):
        return self._background.get_height()
    
    @property
    def width(self):
        return self._background.get_width()

class MouseInteractionSupport(ABC, BackgroundSupport, Positionable):
    """Add a support for clicking and hovering."""

    def __init__(self, background: pygame.Surface, x: int, y: int, layer: int, cursor: pygame.Cursor, overlay: pygame.Surface) -> None:
        ABC.__init__(self)
        BackgroundSupport.__init__(self, background)
        Positionable.__init__(self, x, y, layer)
        self._cursor = cursor
        self._is_mouse_above = False
        self._is_clicking = False
        with open(__CONFIG_FILE, 'r') as f:
            self._default_cursor = json.load(f)['diamond']
    
    def _update_mouse(self, inputs: Inputs, x_frame, y_frame):
        """Update the cursor and do action in case of click."""
        clicks = inputs.get_clicks(x_frame, y_frame)
        if 0 in clicks:
            click = clicks[0]
            if self.x <= click.x <= self.x + self.width and self.y <= click.y <= self.y + self.height:
                pygame.mouse.set_cursor(self._cursor)
                self._is_mouse_above = True
            else:
                self._is_mouse_above = False
        if 1 in clicks and not clicks[1].up:
            click = clicks[0]
            if self.x <= click.x <= self.x + self.width and self.y <= click.y <= self.y + self.height:
                self._is_clicking = True
        if 1 in clicks and clicks[1].up and self._is_clicking:
            self._is_clicking = False



class FocusSupport(ABC, BackgroundSupport):
    """
    Add focus support for the widget, use it as parent class alongside BaseWidget for your widgets.
    use _get_f_background() to get the background. It is either the focus background defined in
    this class or the normal background if the widget is not focused.
    """
    def __init__(self, background: pygame.Surface, focus_background: pygame.Surface = None, initial_focus = False) -> None:
        """
        Add focus support for a widget.

        Params:
        ---
        background: Surface, the background.
        focus_background: Surface, Another background that will be returned as background if the widget is focused.
        if None, use the same image in both case. The focus_background will be reshaped with the background shape.
        initial_focus: bool. If True, the widget is focused at creation.
        """
        ABC.__init__(self)
        BackgroundSupport.__init__(self, background)
        if focus_background is None:
            self._focus_background = self._background.copy()
        else:
            self._focus_background = pygame.transform.scale(focus_background, (self.width, self.height))
        self._focus = initial_focus
    
    def focus(self):
        """Set the focus to the widget."""
        self._focus = True
    
    def unfocus(self):
        """Remove the focus to the widget."""
        self._focus = False
    
    def is_focused(self):
        """Return true if the widget is focused, false otherwise."""
        return self._focus
    
    def _get_f_background(self):
        """Return the focus background if the widget has focus, the normal background otherwise."""
        return self._focus_background.copy() if self.is_focused() else self._background.copy()

class ClickSupport(ABC, BackgroundSupport):
    pass

class DisableSupport(ABC, BackgroundSupport):
    """
    Add enable/disable support for the widget, use it as parent class alongside BaseWidget for your widgets.
    use _get_d_background() to get the background. It is either the focus background defined in
    this class or the normal background if the widget is not focused.
    """
    def __init__(self, background: pygame.Surface, disable_background: pygame.Surface = None, initially_disabled = False) -> None:
        ABC.__init__(self)
        BackgroundSupport.__init__(self, background)
        if disable_background is None:
            self._disable_background = self._background.copy()
        else:
            self._disable_background = pygame.transform.scale(disable_background, (self.width, self.height))
        self._disabled = initially_disabled
    
    def disable(self):
        """Disable the widget."""
        self._focus = True
    
    def enable(self):
        """Enable the widget."""
        self._focus = False
    
    def is_disabled(self):
        """Return true if the widget is disabled, false otherwise."""
        return self._disabled
    
    def _get_d_background(self):
        """Return the disabled background if the widget is disabled, the normal background otherwise."""
        return self._disable_background.copy() if self.is_disabled() else self._background.copy()

class HitboxSupport(ABC, BackgroundSupport, Positionable):
    """
    Add a hitbox to the widget, use it as parent class alongside BaseWidget for your widgets.
    use is_touching(self, x, y) to know if a point x,y is touching the widget.
    use is_touching(self, rect) to know if a rectangle is overlapping with the hitbox.
    use is_touching(self, hitbox, hitbox_x, hitbox_y) to know if another hitbox is touching this one.
    use a FittedHitBoxSupport to use a more precise hitbox, use this one to have a rectangle hitbox.
    """

    def __init__(self, background: pygame.Surface, x:int, y:int, layer: int) -> None:
        """
        Add a hitbox to the widget. The hitbox is the rectangle of the background, represented as numpy matrix of bools.

        Params:
        ---
        background: Surface, the surface of the widget.
        x: int, y: int the position of the widget.
        layer: int, the layer of the widget
        """
        ABC.__init__(self)
        BackgroundSupport.__init__(self, background)
        Positionable.__init__(self, x, y, layer)
        self._hitbox = pygame.surfarray.array_alpha(self._background) >= 0

    def get_hitbox(self) -> np.ndarray:
        """Get the hitbox."""
        return self._hitbox

    def get_rectangle_hitbox(self) -> pygame.rect.Rect:
        """Get the hitbox as a rectangle."""
        return pygame.rect.Rect(self.x, self.y, self.width, self.height)
    
    @overload
    def is_touching(self, position: tuple[int, int]):
        """Return True if the position is in the hitbox."""
        x = int(position[0] - self.x)
        y = int(position[1] - self.y)
        if 0 <= x <= self._hitbox.shape[0] and 0 <= y <= self._hitbox.shape[1]:
            return self._hitbox[x,y]
        return False

    @overload
    def is_touching(self, rect: pygame.rect.Rect):
        """Return True if the rectangle is in contact with the hitbox."""
        x_min = rect.topleft[0] - self.x
        y_min = rect.topleft[1] - self.y
        x_max = rect.bottomright[0] - self.x
        y_max = rect.bottomright[1] - self.y
        for x in range(x_min, x_max+1):
            for y in range(y_min, y_max+1):
                if 0 <= x <= self._hitbox.shape[0] and 0 <= y <= self._hitbox.shape[1] and self._hitbox[x,y]:
                    return True
        return False
    
    @overload
    def is_touching(self, hitbox: np.ndarray[bool], hitbox_left: int, hitbox_top: int):
        """Return True if the rectangle is in contact with the hitbox."""
        other_width, other_height = hitbox.shape
        
        widget_right = self.x + self.width
        widget_bottom = self.y + self.height

        hitbox_right = hitbox_left + other_width
        hitbox_bottom = hitbox_top + other_height
        
        if hitbox_right <= self.x or widget_right <= hitbox_left or widget_bottom <= hitbox_top or hitbox_bottom <= self.y:
            # no overlapping
            return False 
        
        inter_left = max(self.x, hitbox_left)
        inter_right = min(widget_right, hitbox_right)
        inter_top = max(self.y, hitbox_top)
        inter_bottom = min(widget_bottom, hitbox_bottom)
        
        offset_widget_x = inter_left - self.x
        offset_widget_y = inter_top - self.y
        offset_hitbox_x = inter_left - hitbox_left
        offset_hitbox_y = inter_top - hitbox_top
        
        # verify if within the intersection, two hitboxes collides.
        for i in range(inter_bottom - inter_top):
            for j in range(inter_right - inter_left):
                if self._hitbox[offset_widget_x + i, offset_widget_y + j] and hitbox[offset_hitbox_x + i, offset_hitbox_y + j]:
                    return True
        return False

class FittedHitboxSupport(ABC, HitboxSupport):
    """
    Add a fitted hitbox to the widget. The hitbox is the pixels having an alpha above a threshold.
    """
    def __init__(self, background: pygame.Surface, x: int, y: int, layer: int, threshold: int = 50) -> None:
        """
        Add a hitbox to the widget.

        Params:
        ---
        background: Surface, the surface of the widget.
        x: int, y: int the position of the widget.
        layer: int, the layer of the widget
        threshold: the alpha threshold to create the hitbox. The hitbox is the pixels having alpha >= threshold.
        """
        ABC.__init__(self)
        HitboxSupport.__init__(self, background, x, y, layer)
        self._hitbox = pygame.surfarray.array_alpha(self._background) >= threshold