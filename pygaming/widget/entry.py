"""The entry class is an object on which you can write some words"""
import pygame
from .base_widget import BaseWidget
from .supports import FocusSupport, DisableSupport, MouseInteractionSupport, TextSupport
from ...io_.file import FontFile
from ..inputs import Inputs
from ...utils.color import Color, black, full_transparency
from typing import Optional
from ..utils import make_background


def _get_entry_shape(font: pygame.font.Font, length: int, margin_x, margin_y):
    """Calculate the shape of the entry object."""
    mmm: pygame.Surface = font.render("lm"*(length//2) + "n"*(length%2), True, (0,0,0))
    height = mmm.get_height() + 2*margin_y
    width = mmm.get_width() + 2*margin_x
    return width, height

class Entry(BaseWidget, FocusSupport, DisableSupport, MouseInteractionSupport, TextSupport):
    """An Entry widget is used to enter text in the game."""

    def __init__(
        self,
        frame,
        x: int, # pixels
        y: int, # pixels
        font_file: FontFile,
        initial_value = "",
        background: pygame.Surface | Color = full_transparency,
        focus_background: Optional[pygame.Surface | Color] = None,
        disabled_background: Optional[pygame.Surface | Color] = None,
        length: int = 15,
        margin_x: int = 10, # pixels
        margin_y: int = 5, # pixels
        layer: int = 0,
        forbidden_characters: str = '',
        extra_accepted_characters: str = '',
        font_color: Color = black,
        font_size: int = 20,
        italic: bool = False,
        bold: bool = False,
        underline: bool = False,
        antialias: bool = True,
        caret_blink_period: int = 1000, # [milisecondes]
        caret_width = 2, # pixels
        hover_cursor: pygame.Cursor = None,
    ) -> None:
        """
        An entry is a widget used to enter a textual value.

        Params:
        ----
        font_file: FontFile. The font used to display the text.
        x: int, y: int. The coordinate of the top-left corner of the entry in the frame.
        frame: Frame. The frame the entry will be displayed in.
        initial_value: str. The initial value of the entry.
        font_size: the size of the text.
        background: Surface | Color. If a Surface is provided, the top left part of the surface is used
        as background for the text. If a color is provided, fill a surface with the color.
        length: The maxiumum number of characters the text can have.
        margin_x, margin_y: the margin of text in its background (in pixel)
        font_color: The color of the font
        forbidden_characters: the list of forbidden characters.
        text_flags: TextFlags. flags for the text.
        caret_blink_period:int (ms) The period of display the caret.
        The caret is the vertical cursor that show where the next character will be placed,
        The caret will be should per caret_blink_period/2 ms then hidden for caret_blink_period/2 ms.
        caret_width: int. The width of the caret, in pixel.
        initial_focus: bool. If false, you have to click to set the focus on the entry before interacting with.
        """
        width, height = _get_entry_shape(font_file.get(font_size), length, margin_x, margin_y)
        bg = make_background(background, width, height, None)
        
        focus_bg = make_background(focus_background, width, height, bg)
        disable_bg = make_background(disabled_background, width, height, bg)

        BaseWidget.__init__(self, frame, x, y, layer)
        FocusSupport.__init__(self, bg, focus_bg)
        DisableSupport.__init__(self, bg, disable_bg)
        MouseInteractionSupport.__init__(self, bg, x, y, layer, hover_cursor)
        TextSupport.__init__(self, font_color, font_file, font_size, italic, bold, underline, antialias)
        
        self.length = length
        self._font_color = font_color.to_RGBA()

        self._forbidden_characters = forbidden_characters
        self._extra_accepted_characters = extra_accepted_characters

        self._value = initial_value
        self._cursor_index = len(self._value)

        self._caret_blink_period = caret_blink_period/2
        self._caret_width = caret_width
        self._time_since_last_blink = 0
        self._show_caret = True
        self._update_caret_position()
    
    
    def set_color(self, font_color: Color):
        self._font_color = font_color.to_RGBA()
        return TextSupport.set_color(font_color)
    
    def clear(self):
        """Clear the value of the entry"""
        self._value = ""
        self._update_caret_position()
    
    def set(self, value: str):
        """Set the value to a specific value."""
        self._value = str(value)
        self._cursor_index = len(value)
        self._update_caret_position()

    def update(self, inputs: Inputs, loop_duration: int, x_frame, y_frame):
        """Update the entry."""
        if self._focus:
            letters = inputs.get_characters(self._extra_accepted_characters)
            if letters:
                letter = letters[0]
                if letter not in self._forbidden_characters:
                    self._add_letter(letter)
            if inputs.get_keydown(pygame.K_BACKSPACE):
                self._remove_letter()
            arrows = inputs.get_arrows()
            if (pygame.KEYDOWN, pygame.K_RIGHT) in arrows:
                self._move_cursor_to_the_right()
            if (pygame.KEYDOWN, pygame.K_LEFT) in arrows:
                self._move_cursor_to_the_left()

            self._time_since_last_blink += loop_duration
            if self._time_since_last_blink > self._caret_blink_period:
                self._show_caret = not self._show_caret
                self._time_since_last_blink = 0

    def _update_caret_position(self):
        """Get the position of the caret in the image."""
        left_text: pygame.Surface = self._render(self._value[:self._cursor_index])
        self._caret_pos = left_text.get_width()
        self._caret_height = left_text.get_height() + 6

    def get(self) -> str:
        """Get the textual content of the entry"""
        return self._value

    def get_surface(self) -> pygame.Surface:
        """Get the surface of the object to be displayed."""
        background = self._get_background()
        text = self._render(self._value)
        left = max(self.width // 2 - text.get_width()//2, 0)
        up = self.height // 2 - text.get_height()//2 
        background.blit(text, (left, up))
        if self._show_caret and self._focus:
            start_pos = left + self._caret_pos -1, (self.height - self._caret_height)//2
            end_pos = left + self._caret_pos -1, (self.height + self._caret_height)//2
            pygame.draw.line(background, self._font_color, start_pos, end_pos, self._caret_width)
        return background

    def _add_letter(self, letter: str):
        """Add a letter in the text value"""
        if len(self._value) < self.length:
            letters = list(self._value)
            letters.insert(self._cursor_index, letter)
            self._value = "".join(letters)
            self._cursor_index += 1
            self._update_caret_position()

    def _remove_letter(self):
        """Remove the letter."""
        if self._value and self._cursor_index:
            letters = list(self._value)
            letters.pop(self._cursor_index-1)
            self._value = "".join(letters)
            self._cursor_index -= 1
            self._update_caret_position()
    
    def _move_cursor_to_the_right(self):
        """Move cursor to the right"""
        if self._cursor_index < len(self._value):
            self._cursor_index += 1
            self._time_since_last_blink = 0
            self._show_caret = True
            self._update_caret_position()

    def _move_cursor_to_the_left(self):
        """Move cursor to the left"""
        if self._cursor_index > 0:
            self._cursor_index -= 1
            self._time_since_last_blink = 0
            self._show_caret = True
            self._update_caret_position()
