"""The entry class is an object on which you can write some words"""
import pygame
from ...io_.file import FontFile
from ..inputs import Inputs
from ...utils.color import Color
from .base_widget import BaseWidget

def _get_entry_shape(font: pygame.font.Font, size: int):
    mmm: pygame.Surface = font.render("lm"*(size//2), True, (0,0,0))
    height = int(mmm.get_height()*1.05)
    width = mmm.get_width() + 20
    return width, height

class Entry(BaseWidget):
    """An Entry widget is used to enter text in the game, like entries in tkinter."""

    def __init__(
        self,
        font_file: FontFile,
        x: int,
        y: int,
        frame,
        initial_value = "",
        font_size: int = 20,
        background: pygame.Surface | Color = Color(255,255,255),
        size: int = 10,
        font_color: Color = Color(0,0,0),
        bold: bool = False,
        underline: bool = False,
        italic: bool = False,
        antialias: bool = True,
        caret_blink_period: int = 1000, # [milisecondes]
        caret_width = 2, # pixel
        initial_focus=False
    ) -> None:
        """
        An entry is a widget used to enter a textual value.

        """
        self.font = font_file.get(font_size, italic, bold, underline)
        width, height = _get_entry_shape(self.font, size)
        if isinstance(background, Color):
            bg = pygame.Surface((width, height))
            bg.fill(background.to_RGBA())
        else:
            bg = background
        super().__init__(frame, x, y, width, height, bg, initial_focus)
        
        self.font_color = font_color.to_RGBA()
        self.x, self.y = x,y
        self.size = size
        self.antialias = antialias

        self._value = initial_value
        self._cursor_index = len(self._value)

        self._caret_blink_period = caret_blink_period/2
        self._caret_width = caret_width
        self._time_since_last_blink = 0
        self._show_caret = True
        self._caret_pos = self._get_caret_position()

    def update(self, inputs: Inputs, loop_duration: int):
        """Update the entry."""
        if self._focus:
            letters = inputs.get_characters()
            if letters:
                letter = letters[0]
                self._add_letter(letter)
            if inputs.get_keydown(pygame.K_BACKSPACE):
                self._remove_letter()
            self._time_since_last_blink += loop_duration
            if self._time_since_last_blink > self._caret_blink_period:
                self._show_caret = not self._show_caret
                self._time_since_last_blink = 0
            arrows = inputs.get_arrows()
            if (pygame.KEYDOWN, pygame.K_RIGHT) in arrows:
                self._move_cursor_to_the_right()
            if (pygame.KEYDOWN, pygame.K_LEFT) in arrows:
                self._move_cursor_to_the_left()

    def _get_caret_position(self):
        """Get the position of the caret in the image."""
        left_text: pygame.Surface = self.font.render(self._value[:self._cursor_index], self.antialias, (0,0,0))
        return left_text.get_width()

    def get(self) -> str:
        """Get the textual content of the entry"""
        return self._value

    def get_surface(self) -> pygame.Surface:
        """Get the surface of the object to be displayed."""
        background = self.background.copy()
        text = self.font.render(self._value, self.antialias, self.font_color)
        left = max(self.width // 2 - text.get_width()//2, 0)
        up = self.height // 2 - text.get_height()//2 
        background.blit(text, (left, up))
        if self._show_caret:
            start_pos = left + self._caret_pos, 2
            end_pos = left + self._caret_pos, self.height - 2
            pygame.draw.line(background, self.font_color, start_pos, end_pos, self._caret_width)
        return background

    def _add_letter(self, letter: str):
        """Add a letter in the text value"""
        if len(self._value) < self.size:
            letters = list(self._value)
            letters.insert(self._cursor_index, letter)
            self._value = "".join(letters)
            self._cursor_index += 1
            self._caret_pos = self._get_caret_position()

    def _remove_letter(self):
        """Remove the letter."""
        if self._value and self._cursor_index:
            letters = list(self._value)
            letters.pop(self._cursor_index-1)
            self._value = "".join(letters)
            self._cursor_index -= 1
            self._caret_pos = self._get_caret_position()
    
    def _move_cursor_to_the_right(self):
        """Move cursor to the right"""
        if self._cursor_index < len(self._value):
            self._cursor_index += 1
            self._time_since_last_blink = 0
            self._show_caret = True
            self._caret_pos = self._get_caret_position()

    def _move_cursor_to_the_left(self):
        """Move cursor to the left"""
        if self._cursor_index > 0:
            self._cursor_index -= 1
            self._time_since_last_blink = 0
            self._show_caret = True
            self._caret_pos = self._get_caret_position()
