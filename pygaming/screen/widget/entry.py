"""Then entry module contains the entry widget."""
from typing import Optional
from pygame import Surface, draw
from .widget import Widget
from ..anchors import TOP_LEFT, CENTER, Anchor
from ..frame import Frame
from ...color import Color
from ..art import Art
from ...cursor import Cursor
from ..tooltip import Tooltip
from ..hitbox import Hitbox

class Entry(Widget):
    """The Entry widget is used to allow the user to add a textual input."""

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: Art,
        normal_font: str,
        normal_font_color: Color,
        focused_background: Optional[Art] = None,
        focused_font: Optional[str] = None,
        focused_font_color: Optional[str] = None,
        disabled_background: Optional[Art] = None,
        disabled_font: Optional[str] = None,
        disbaled_font_color: Optional[str] = None,
        initial_value: str = '',
        extra_characters: str = '',
        forbid_characters: str = '',
        anchor: Anchor = TOP_LEFT,
        active_area: Optional[Hitbox] = None,
        layer: int = 0,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        justify: Anchor = CENTER,
        caret_frequency: int = 500,
        caret_width: int = 2,
        max_length: int = 10,
        update_if_invisible: bool = False,
        empty_text_or_loc: str = "",
        empty_font: str = None,
        empty_font_color: str = None,
    ) -> None:
        """
        The Entry widget is used to allow the user to add a textual input.
        
        Params:
        ---
        - master: Frame. The Frame in which this widget is placed.
        - x: int, the coordinate of the anchor in the master Frame
        - y: int, the top coordinate of the anchor in the master Frame.
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
        - anchor: tuple[float, float]. The point of the slider that is placed at the coordinate (x,y).
          Use TOP_LEFT, TOP_RIGHT, CENTER, BOTTOM_LEFT or BOTTOM_RIGHT, or another personized tuple.
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the slider. if None, then it is the whole background.
        - layer: int, the layer of the slider in its master frame
        - tooltip: Tooltip, The tooltip to show when the slider is hovered.
        - cursor: Cursor The cursor of the mouse to use when the widget is hovered,
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - justify: str, the position of the text in the entry. can be TEXT_CENTERED, TEXT_RIGHT, TEXT_LEFT
        - caret_frequency: int, The blinking frequency of the caret (ms)
        - caret_width: int, The width of the caret in pixel.
        - max_length: The maximum number of characters the entry can support.
        """

        super().__init__(
            master,
            x,
            y,
            normal_background,
            focused_background,
            disabled_background,
            anchor,
            active_area,
            layer,
            tooltip,
            cursor,
            continue_animation,
            update_if_invisible
        )

        self._text = str(initial_value)
        self.extra_characters = extra_characters
        self.forbid_characters = forbid_characters
        self._normal_font = normal_font
        if focused_font is None:
            focused_font = normal_font
        self._focused_font = focused_font
        if disabled_font is None:
            disabled_font = normal_font
        self._disabled_font = disabled_font

        self._normal_font_color = normal_font_color
        if focused_font_color is None:
            focused_font_color = normal_font_color
        self._focused_font_color = focused_font_color
        if disbaled_font_color is None:
            disbaled_font_color = normal_font_color
        self._disabled_font_color = disabled_font

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

    def start(self):
        """Nothing to do at the start of the phase for this widget."""

    def end(self):
        """Nothing to do at the end of the phase for this widget."""

    def get(self):
        """Return the textual value currently entered."""
        return self._text

    def _make_disabled_surface(self) -> Surface:
        return self._make_surface(
            self.disabled_background.get(self.background if self._continue_animation else None),
            self._disabled_font, self._disabled_font_color, False, self._text
        )

    def _make_focused_surface(self) -> Surface:
        return self._make_surface(
            self.focused_background.get(self.background if self._continue_animation else None),
            self._focused_font, self._focused_font_color, self._show_caret, self._text
        )

    def _make_normal_surface(self) -> Surface:
        if self._text: # if the current text is not empty
            return self._make_surface(
                self.normal_background.get(None, **self.game.settings),
                self._normal_font, self._normal_font_color, False, self._text
            )
        return self._make_surface(
            self.normal_background.get(None, **self.game.settings),
            self._empty_font, self._empty_font_color, False, self._empty_text_or_loc
        )

    def _make_surface(self, background: Surface, font: str, color: Color, caret: bool, text: str):
        rendered_text = self.game.typewriter.render(font, text, color)
        text_width, text_height = rendered_text.get_size()
        just_y = self._justify[1]*(background.get_height() - text_height)
        # if the text is too long, we center on the charet, if the charet is too much on the right or left, we let the first/last
        # character be on the left/right.
        if text_width > background.get_width():
            just_x = min(0, -self.game.typewriter.size(font, self._text[:self._caret_index])[0] + background.get_width()//2)
            just_x = max(just_x, background.get_width() - text_width)
        else:
            just_x = self._justify[0]*(background.get_width() - text_width)
        background.blit(rendered_text, (just_x, just_y))
        if caret:
            caret_height = self.game.typewriter.get_linesize(font)
            caret_x = just_x + self.game.typewriter.size(font, self._text[:self._caret_index])[0]
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

            # Modify the text if a character is typed
            new_characters = ''.join(self.game.keyboard.get_characters(self.extra_characters, self.forbid_characters))
            self.add_new_characters(new_characters)

            # Move the caret if an arrow is tapped.
            if self.game.keyboard.actions_down['left']:
                self.move_to_the_left()
            if self.game.keyboard.actions_down['right']:
                self.move_to_the_right()

            if self.game.keyboard.actions_down['backspace']:
                self.del_one()
        else:
            self._show_caret = True

    def add_new_characters(self, new_characters):
        """Add new characters to the value."""
        margin = self.max_length - len(self._text)
        if margin < len(new_characters):
            new_characters = new_characters[:margin]

        if new_characters:
            self._text = self._text[:self._caret_index] + new_characters + self._text[self._caret_index:]
            self._caret_index += len(new_characters)
            self.notify_change()

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
