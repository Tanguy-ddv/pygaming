"""Then entry module contains the entry widget."""
from typing import Optional, Callable, Any, Literal
from pygame import Surface, draw, Rect
from .widget import Widget
from ..anchors import LEFT, AnchorLike, Anchor
from ..frame import Frame
from ...color import Color
from ..art import Art
from ...cursor import Cursor
from ..tooltip import Tooltip
from ..hitbox import Hitbox

_DEFAULT_CARET_FREQUENCY = 500 # [ms]
_DEFAULT_CARET_WIDTH = 2 # [px]
_DEFAULT_MAX_LENGTH = 15
_PASSWORD_CHAR = "\u2022"
_DEFAULT_PAD = 2

class Entry(Widget):
    """The Entry widget is used to allow the user to add a textual input."""

    def __init__(
        self,
        master: Frame,
        normal_background: Art,
        normal_font: str,
        normal_font_color: Color,
        focused_background: Optional[Art] = None,
        focused_font: Optional[str] = None,
        focused_font_color: Optional[Color] = None,
        disabled_background: Optional[Art] = None,
        disabled_font: Optional[str] = None,
        disabled_font_color: Optional[Color] = None,
        hovered_background: Optional[str] = None,
        hovered_font: Optional[str] = None,
        hovered_font_color: Optional[Color] = None,
        initial_value: str = '',
        extra_characters: str = '',
        forbid_characters: str = '',
        active_area: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        justify: AnchorLike = LEFT,
        caret_frequency: int = _DEFAULT_CARET_FREQUENCY,
        caret_width: int = _DEFAULT_CARET_WIDTH,
        max_length: int = _DEFAULT_MAX_LENGTH,
        update_if_invisible: bool = False,
        empty_text_or_loc: str = "",
        empty_font: Optional[str] = None,
        empty_font_color: Optional[str] = None,
        command: Optional[Callable[[], Any]] = None,
        password: bool = False
    ) -> None:
        """
        The Entry widget is used to allow the user to add a textual input.
        
        Params:
        ---
        - master: Frame. The Frame in which this widget is placed.
        - normal_background: AnimatedSurface | Surface: The surface used as the background of the slider when it is neither focused nor disabled.
        - normal_font: str
        - normal_font_color: Color
        - focused_background: AnimatedSurface | Surface: The surface used as the background of the slider when it is focused.
        - focused_font: str,
        - focused_font_color: Optional[str] = None,
        - disabled_background: AnimatedSurface | Surface: The surface used as the background of the slider when it is disabled.
        - disabled_font: str,
        - disbaled_font_color: Optional[str] = None,
        - initial_value: str
        - extra_characters: str
        - forbid_charcaters: str
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the slider. if None, then it is the whole background.
        - tooltip: Tooltip, The tooltip to show when the slider is hovered.
        - cursor: Cursor The cursor of the mouse to use when the widget is hovered,
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - justify: AnchorLike, the position of the text in the entry.
        - caret_frequency: int, The blinking frequency of the caret (ms)
        - caret_width: int, The width of the caret in pixel.
        - max_length: The maximum number of characters the entry can support.
        """

        super().__init__(
            master,
            normal_background,
            focused_background,
            disabled_background,
            hovered_background,
            active_area,
            tooltip,
            cursor,
            continue_animation,
            update_if_invisible
        )

        self._text = str(initial_value)
        self.extra_characters = extra_characters
        self.forbid_characters = forbid_characters + '\n'

        self._command = command
        self.password = password

        self._normal_font = normal_font

        if focused_font is None:
            focused_font = normal_font
        self._focused_font = focused_font
        if disabled_font is None:
            disabled_font = normal_font
        self._disabled_font = disabled_font
        if hovered_font is None:
            hovered_font = normal_font
        self._hovered_font = hovered_font

        self._normal_font_color = normal_font_color
        if focused_font_color is None:
            focused_font_color = normal_font_color
        self._focused_font_color = focused_font_color
        if disabled_font_color is None:
            disabled_font_color = normal_font_color
        self._disabled_font_color = disabled_font_color
        if hovered_font_color is None:
            hovered_font_color = normal_font_color
        self._hovered_font_color = hovered_font_color

        self.max_length = max_length

        self._justify = Anchor(justify)
        self._caret_width = caret_width

        self._caret_index = len(self._text)
        self._caret_frequency = caret_frequency
        self._show_caret = True
        self._caret_delta = 0

        self._empty_text_or_loc = empty_text_or_loc
        self._empty_font = empty_font if empty_font is not None else self._normal_font
        self._empty_font_color = empty_font_color if empty_font_color is not None else self._normal_font_color

    def set_text(self, new_text: str):
        """Set a new value for the entry."""
        self._text = str(new_text)
        self.notify_change()

    def get(self):
        """Return the textual value currently entered."""
        return self._text

    def __make_text_to_display(self):
        return self._text if not self.password else _PASSWORD_CHAR*len(self._text)

    def _make_disabled_surface(self) -> Surface:
        return self.__make_surface(
            self.disabled_background.get(self.background if self._continue_animation else None, **self.game.settings),
            self._disabled_font, self._disabled_font_color, False, self.__make_text_to_display()
        )

    def _make_focused_surface(self) -> Surface:
        return self.__make_surface(
            self.focused_background.get(self.background if self._continue_animation else None, **self.game.settings),
            self._focused_font, self._focused_font_color, self._show_caret, self.__make_text_to_display()
        )

    def _make_normal_surface(self) -> Surface:
        if self._text: # if the current text is not empty
            return self.__make_surface(
                self.normal_background.get(None, **self.game.settings),
                self._normal_font, self._normal_font_color, False, self.__make_text_to_display()
            )
        return self.__make_surface(
            self.normal_background.get(None, **self.game.settings),
            self._empty_font, self._empty_font_color, False, self._empty_text_or_loc
        )

    def _make_hovered_surface(self) -> Surface:
        if self._text: # if the current text is not empty
            return self.__make_surface(
                self.hovered_background.get(None, **self.game.settings),
                self._hovered_font, self._hovered_font_color, False, self.__make_text_to_display()
            )
        return self.__make_surface(
            self.hovered_background.get(None, **self.game.settings),
            self._empty_font, self._empty_font_color, False, self._empty_text_or_loc
        )

    def __make_surface(self, background: Surface, font: str, color: Color, caret: bool, text: str):
        rendered_text = self.game.typewriter.render(font, text, color)
        text_width, text_height = rendered_text.get_size()
        just_y = self._justify[1]*(background.get_height() - text_height)
        # if the text is too long, we center on the charet, if the charet is too much on the right or left, we let the first/last
        # character be on the left/right.
        if text_width > background.get_width():
            just_x = min(0, -self.game.typewriter.size(font, text[:self._caret_index])[0] + background.get_width()//2)
            just_x = max(just_x, background.get_width() - text_width)
        else:
            just_x = self._justify[0]*(background.get_width() - text_width)
        background.blit(rendered_text, (just_x, just_y))
        if caret:
            caret_height = self.game.typewriter.get_linesize(font)
            caret_x = just_x + self.game.typewriter.size(font, text[:self._caret_index])[0]
            draw.line(background, self._focused_font_color, (caret_x, just_y), (caret_x, just_y + caret_height), self._caret_width)
        return background

    def update(self, loop_duration: int):
        """Update the entry with the inputs."""
        # Update the caret
        if self.focused and not self.disabled:
            self._caret_delta += loop_duration/self._caret_frequency
            if self._caret_delta > 1:
                self.notify_change()
                self._caret_delta = 0
                self._show_caret = not self._show_caret

            # Modify the text if a character is entered
            new_characters = ''.join(self.game.keyboard.get_characters(self.extra_characters, self.forbid_characters))
            command_called = self._add_new_characters(new_characters)
            if new_characters and self._command is not None:
                self._command()

            # Move the caret if an arrow is pressed.
            if self.game.keyboard.actions_down['left']:
                self.move_to_the_left()
            if self.game.keyboard.actions_down['right']:
                self.move_to_the_right()

            if self.game.keyboard.actions_down['backspace']: # Delete one caracter.
                self.del_one()
                if self._command is not None and not command_called:
                    self._command()
        else:
            self._show_caret = True

    def _add_new_characters(self, new_characters):
        """Add new characters to the value. Return True if some new characters have been added."""
        margin = self.max_length - len(self._text)
        if margin < len(new_characters):
            new_characters = new_characters[:margin]

        if new_characters:
            self._text = self._text[:self._caret_index] + new_characters + self._text[self._caret_index:]
            self._caret_index += len(new_characters)
            self.notify_change()
            return True
        return False

    def del_one(self):
        """Delete a character."""
        if self._caret_index > 0:
            self._text = self._text[:self._caret_index - 1] + self._text[self._caret_index:]
            self._caret_index -= 1
            self.notify_change()

    def move_to_the_right(self):
        """Move the caret to the right."""
        if self._caret_index < len(self._text):
            self._caret_index += 1
            self.notify_change()

    def move_to_the_left(self):
        """Move the caret to the left."""
        if self._caret_index > 0:
            self._caret_index -= 1
            self.notify_change()

class Text(Widget):
    """A Text widget is a multiline text area where the player can write multiple lines."""

    
    def __init__(
        self,
        master: Frame,
        normal_background: Art,
        normal_font: str,
        normal_font_color: Color,
        focused_background: Optional[Art] = None,
        focused_font: Optional[str] = None,
        focused_font_color: Optional[Color] = None,
        disabled_background: Optional[Art] = None,
        disabled_font: Optional[str] = None,
        disabled_font_color: Optional[Color] = None,
        hovered_background: Optional[str] = None,
        hovered_font: Optional[str] = None,
        hovered_font_color: Optional[Color] = None,
        initial_value: str = '',
        extra_characters: str = '',
        forbid_characters: str = '',
        active_area: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        justify: Literal[Anchor.LEFT, Anchor.RIGHT, Anchor.CENTER, None] = Anchor.LEFT,
        caret_frequency: int = _DEFAULT_CARET_FREQUENCY,
        caret_width: int = _DEFAULT_CARET_WIDTH,
        max_length: int = _DEFAULT_MAX_LENGTH,
        update_if_invisible: bool = False,
        empty_text_or_loc: str = "",
        empty_font: Optional[str] = None,
        empty_font_color: Optional[str] = None,
        command: Optional[Callable[[], Any]] = None,
        wrap: bool = True,
    ) -> None:
        
        super().__init__(
            master,
            normal_background,
            focused_background,
            disabled_background,
            hovered_background,
            active_area,
            tooltip,
            cursor,
            continue_animation,
            update_if_invisible
        )

        self._text = str(initial_value)
        self.extra_characters = extra_characters
        self.forbid_characters = forbid_characters

        self._command = command
        self._wrap = wrap

        self._normal_font = normal_font

        if focused_font is None:
            focused_font = normal_font
        self._focused_font = focused_font
        if disabled_font is None:
            disabled_font = normal_font
        self._disabled_font = disabled_font
        if hovered_font is None:
            hovered_font = normal_font
        self._hovered_font = hovered_font

        self._normal_font_color = normal_font_color
        if focused_font_color is None:
            focused_font_color = normal_font_color
        self._focused_font_color = focused_font_color
        if disabled_font_color is None:
            disabled_font_color = normal_font_color
        self._disabled_font_color = disabled_font_color
        if hovered_font_color is None:
            hovered_font_color = normal_font_color
        self._hovered_font_color = hovered_font_color

        self.max_length = max_length

        self._justify = justify
        self._caret_width = caret_width

        self._caret_index = len(self._text)
        self._caret_frequency = caret_frequency
        self._show_caret = True
        self._caret_delta = 0

        self._empty_text_or_loc = empty_text_or_loc
        self._empty_font = empty_font if empty_font is not None else self._normal_font
        self._empty_font_color = empty_font_color if empty_font_color is not None else self._normal_font_color

    def set_text(self, new_text: str):
        """Set a new value for the entry."""
        self._text = str(new_text)
        self.notify_change()

    def get(self):
        """Return the textual value currently entered."""
        return self._text

    def del_one(self):
        """Delete a character."""
        if self._caret_index > 0:
            self._text = self._text[:self._caret_index - 1] + self._text[self._caret_index:]
            self._caret_index -= 1

    def move_to_the_right(self):
        """Move the caret to the right."""
        if self._caret_index < len(self._text):
            self._caret_index += 1

    def move_to_the_left(self):
        """Move the caret to the left."""
        if self._caret_index > 0:
            self._caret_index -= 1

    def move_to_the_bottom(self):
        """Move the caret to the bottom."""

        car_pos = self.game.typewriter.get_caret_pos(
            self._focused_font, self._caret_index, self._text, self._justify, False, self._wrap, self.focused_background.width
        )

        new_pos = car_pos[0], car_pos[1] + self.game.typewriter.get_linesize(self._focused_font)

        self._caret_index = self.game.typewriter.get_caret_index(
            self._focused_font, new_pos, self._text, self._justify, False, self._wrap, self.focused_background.width
        )

    def move_to_the_top(self):
        """Move the caret to the top."""

        car_pos = self.game.typewriter.get_caret_pos(
            self._focused_font, self._caret_index, self._text, self._justify, False, self._wrap, self.focused_background.width
        )

        new_pos = car_pos[0], car_pos[1] - self.game.typewriter.get_linesize(self._focused_font)

        self._caret_index = self.game.typewriter.get_caret_index(
            self._focused_font, new_pos, self._text, self._justify, False, self._wrap, self.focused_background.width
        )

    def _add_new_characters(self, new_characters):
        """Add new characters to the value. Return True if some new characters have been added."""
        margin = self.max_length - len(self._text)
        if margin < len(new_characters):
            new_characters = new_characters[:margin]

        if new_characters:
            self._text = self._text[:self._caret_index] + new_characters + self._text[self._caret_index:]
            self._caret_index += len(new_characters)
            self.notify_change()
            return True
        return False


    def _make_disabled_surface(self) -> Surface:
        return self.__make_surface(
            self.disabled_background.get(self.background if self._continue_animation else None, **self.game.settings),
            self._disabled_font, self._disabled_font_color, False, self._text
        )

    def _make_focused_surface(self) -> Surface:
        return self.__make_surface(
            self.focused_background.get(self.background if self._continue_animation else None, **self.game.settings),
            self._focused_font, self._focused_font_color, self._show_caret, self._text
        )

    def _make_normal_surface(self) -> Surface:
        if self._text: # if the current text is not empty
            return self.__make_surface(
                self.normal_background.get(None, **self.game.settings),
                self._normal_font, self._normal_font_color, False, self._text
            )
        return self.__make_surface(
            self.normal_background.get(None, **self.game.settings),
            self._empty_font, self._empty_font_color, False, self._empty_text_or_loc
        )

    def _make_hovered_surface(self) -> Surface:
        if self._text: # if the current text is not empty
            return self.__make_surface(
                self.hovered_background.get(None, **self.game.settings),
                self._hovered_font, self._hovered_font_color, False, self._text
            )
        return self.__make_surface(
            self.hovered_background.get(None, **self.game.settings),
            self._empty_font, self._empty_font_color, False, self._empty_text_or_loc
        )
    
    def __make_surface(self, background: Surface, font: str, color: Color, caret: bool, text: str):
        rendered_text = self.game.typewriter.render(
            font, text, color, justify=self._justify,
            can_be_loc=len(self._text) == 0, wrap = self._wrap, max_width=background.get_width()
        )
        text_width, _ = rendered_text.get_size()
        # if the text is too long, we center on the charet, if the charet is too much on the right or left, we let the first/last
        # character be on the left/right.
        just_x = self._justify[0]*(background.get_width() - text_width)
        background.blit(rendered_text, (just_x, _DEFAULT_PAD))
        if caret:
            caret_x, caret_y = self.game.typewriter.get_caret_pos(font, self._caret_index, text, self._justify, False, self._wrap, max_width=background.get_width() - _DEFAULT_PAD)
            caret_height = self.game.typewriter.get_linesize(font)
            background.fill(color, Rect(caret_x, caret_y + _DEFAULT_PAD, self._caret_width, caret_height))
        return background
    
    def __reset_caret(self, show: bool):
        self.notify_change()
        self._caret_delta = 0
        self._show_caret = show


    def update(self, loop_duration: int):
        """Update the entry with the inputs."""
        # Update the caret
        if self.focused and not self.disabled:
            self._caret_delta += loop_duration/self._caret_frequency
            if self._caret_delta > 1:
                self.__reset_caret(not self._show_caret)

            # Modify the text if a character is entered
            new_characters = ''.join(self.game.keyboard.get_characters(self.extra_characters, self.forbid_characters))
            command_called = self._add_new_characters(new_characters)
            if new_characters:
                self.__reset_caret(True)
                if self._command is not None:
                    self._command()

            # Move the caret if an arrow is pressed.
            if self.game.keyboard.actions_down['left']:
                self.move_to_the_left()
                self.__reset_caret(True)
            if self.game.keyboard.actions_down['right']:
                self.move_to_the_right()
                self.__reset_caret(True)
            if self.game.keyboard.actions_down['up']:
                self.move_to_the_top()
                self.__reset_caret(True)
            if self.game.keyboard.actions_down['down']:
                self.move_to_the_bottom()
                self.__reset_caret(True)
            if self.game.keyboard.actions_down['backspace']: # Delete one caracter.
                self.del_one()
                self.__reset_caret(True)
                if self._command is not None and not command_called:
                    self._command()

            ck1 = self.game.mouse.get_click(1)
            if self.is_contact(ck1):

                pos = ck1.make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio)
                self._caret_index = self.game.typewriter.get_caret_index(
                    self._focused_font, pos, self._text, self._justify, False, self._wrap, self.background.width
                )
                self.__reset_caret(True)
                
        else:
            self._show_caret = True
