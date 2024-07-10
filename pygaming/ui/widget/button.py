"""A button is a widget used to be clicked. It can only have a value True or False is it is triggered or not."""

import pygame

from pygaming.ui.inputs.inputs import Inputs
from .base_widget import BaseWidget
from .supports import MouseInteractionSupport, TextSupport, DisableSupport, FocusSupport
from typing import Optional, Callable
from ...utils.color import Color, black
from ...io_.file import FontFile
from ..utils import make_background

class Button(BaseWidget, DisableSupport, MouseInteractionSupport, FocusSupport):

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        width: int,
        height: int,
        background: pygame.Surface | Color,
        focus_background: pygame.Surface | Color | None = None,
        active_background: Optional[pygame.Surface | Color] = None,
        disabled_background: Optional[pygame.Surface | Color] = None,
        layer: int = 0,
        on_click_command: Callable = None,
        on_unclick_command: Callable = None,
        active_command: Callable = None,
        unactive_command: Callable = None,
        hover_cursor: pygame.Cursor = None,
    ) -> None:
        """
        Create a button.
        
        Params:
        ---

        """
        bg = make_background(background, width, height, None)
        focus_bg = make_background(focus_background, width, height, bg)
        active_bg = make_background(active_background, width, height, bg)
        disable_bg = make_background(disabled_background, width, height, bg)

        BaseWidget.__init__(self, frame, x, y, layer)
        DisableSupport.__init__(self, bg, disable_bg)
        FocusSupport.__init__(self, bg, focus_bg)
        MouseInteractionSupport.__init__(self, bg, x, y, layer, hover_cursor)
        

        self._on_click_command = on_click_command
        self._on_unclick_command = on_unclick_command
        self._active_command = active_command
        self._unactive_command = unactive_command
        
        self._active_background = active_bg

        self._active = False

    def get_surface(self) -> pygame.Surface:
        """Return the surface of the button to be displayed."""
        if self._active:
            return self._active_background
        else:
            return self._get_background()

    def get(self):
        """Return true if the user is clicking the button."""
        return self._active
    
    def update(self, inputs: Inputs, loop_duration: int, x_frame: int, y_frame: int):
        """Update the button value."""
        if not self._disabled:
            previously_clicking = self._is_clicking
            self._update_mouse(inputs, x_frame, y_frame)
            actions = inputs.get_actions()
            now_clicking = self._is_clicking or ("enter" in actions and actions["enter"] and self._focus)
            self._active = now_clicking
            if now_clicking and previously_clicking:
                if self._active_command is not None:
                    self._active_command()
            elif now_clicking and not previously_clicking:
                if self._on_click_command is not None:
                    self._on_click_command()
            elif not now_clicking and previously_clicking :
                if self._on_unclick_command is not None:
                    self._on_unclick_command()
            else:
                if self._unactive_command is not None:
                    self._unactive_command()

class TextButton(Button, TextSupport):

    def __init__(
        self,
        frame,
        x: int,
        y: int,
        text: str,
        background: pygame.Surface | Color,
        focus_background: pygame.Surface | Color | None = None,
        active_background: pygame.Surface | Color | None = None,
        disabled_background: pygame.Surface | Color | None = None,
        layer: int = 0,
        margin_x: int = 10,
        margin_y: int = 3,
        font_size: int = 15,
        font_color: Color = black,
        font_file: FontFile = None,
        italic: bool = False,
        bold: bool = False,
        underline: bool = False,
        antialias: bool = True,
        on_click_command: Callable = None,
        on_unclick_command: Callable = None,
        active_command: Callable = None,
        unactive_command: Callable = None,
        hover_cursor: pygame.Cursor = None
    ) -> None:

        TextSupport.__init__(self, font_color, font_file, font_size, italic, bold, underline, antialias)

        if text is None:
            text = ""
        text_surface = self._render(text)
        height = text_surface.get_height() + 2* margin_y
        width = text_surface.get_width() + 2* margin_x
        
        Button.__init__(
            self,
            frame,
            x,
            y,
            width,
            height,
            background,
            focus_background,
            active_background,
            disabled_background,
            layer,
            on_click_command,
            on_unclick_command,
            active_command,
            unactive_command,
            hover_cursor
        )

        self._background.blit(text_surface, (margin_x, margin_y))
        self._active_background.blit(text_surface, (margin_x, margin_y))
        self._focus_background.blit(text_surface, (margin_x, margin_y))
        self._disable_background.blit(text_surface, (margin_x, margin_y))
