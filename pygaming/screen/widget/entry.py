"""Then entry module contains the entry widget."""

from typing import Optional
from pygame import Cursor, Rect, Surface
from .widget import Widget
from ..element import SurfaceLike, TOP_LEFT, CENTER
from ..colored_surfaces import ColoredRectangle
from ..frame import Frame
from ...color import Color

class Entry(Widget):
    """The Entry widget is used to allow the user to add a textual input."""

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: SurfaceLike,
        normal_font: str,
        normal_font_color: Color,
        focused_background: Optional[SurfaceLike] = None,
        focused_font: Optional[str] = None,
        focused_font_color: Optional[str] = None,
        disabled_background: Optional[SurfaceLike] = None,
        disabled_font: Optional[str] = None,
        disbaled_font_color: Optional[str] = None,
        initial_value: str = '',
        extra_characters: str = '',
        forbid_characters: str = '',
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Rect | None = None,
        layer: int = 0,
        hover_surface: Surface | None = None,
        hover_cursor: Cursor | None = None,
        continue_animation: bool = False,
        justify = CENTER,
        charet_frequency: int = 500,
        charet_width: int = 2,
        max_length: int = 10,
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
        - hover_surface: Surface, The surface to show when the slider is hovered.
        - hover_cursor: Cursor The cursor of the mouse to use when the widget is hovered,
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - justify: str, the position of the text in the entry. can be TEXT_CENTERED, TEXT_RIGHT, TEXT_LEFT
        - charet_frequency: int, The blinking frequency of the charet (ms)
        - charet_width: int, The width of the charet in pixel.
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
            hover_surface,
            hover_cursor,
            continue_animation
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
        self._charet_index = len(self._text)
        self._charet_frequency = charet_frequency
        self._charet = ColoredRectangle(self._focused_font_color, charet_width, self.game.typewriter.get_linesize(self._focused_font))

        self._show_caret = True
        self._charet_delta = 0

    def set_text(self, new_text: str):
        """Set a new value for the entry."""
        self._text = str(new_text)

    def get(self):
        """Return the textual value currently entered."""
        return self._text

    def _get_disabled_surface(self) -> Surface:
        return self._get_surface(self.disabled_background.get(), self._disabled_font, self._disabled_font_color, False)

    def _get_focused_surface(self) -> Surface:
        return self._get_surface(self.focused_background.get(), self._focused_font, self._focused_font_color, self._show_caret)

    def _get_normal_surface(self) -> Surface:
        return self._get_surface(self.normal_background.get(), self._normal_font, self._normal_font_color, False)

    def _get_surface(self, background: Surface, font: str, color: Color, charet: bool):
        rendered_text = self.game.typewriter.render(font, self._text, color)
        text_width, text_height = rendered_text.get_size()
        just_x = self._justify[0]*(background.get_width() - text_width)
        just_y = self._justify[1]*(background.get_height() - text_height)
        background.blit(rendered_text, (just_x, just_y))
        if charet:
            charet_x = just_x + self.game.typewriter.size(font, self._text[:self._charet_index])[0]
            background.blit(self._charet, (charet_x, just_y))
        return background

    def update(self, loop_duration: int):
        """Update the entry with the inputs."""
        # Update the charet
        if self.focused:
            self._charet_delta += loop_duration/self._charet_frequency
            if self._charet_delta > 1:
                self._charet_delta = 0
                self._show_caret = not self._show_caret

            # Modify the text if a character is typed
            new_characters = ''.join(self.game.keyboard.get_characters(self.extra_characters, self.forbid_characters))
            self.add_new_characters(new_characters)

            # Move the charet if an arrow is tapped.
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
            self._text = self._text[:self._charet_index] + new_characters + self._text[self._charet_index:]
            self._charet_index += len(new_characters)

    def del_one(self):
        """Delete a character."""
        if self._charet_index > 0:
            self._text = self._text[:self._charet_index - 1] + self._text[self._charet_index:]
            self._charet_index -= 1

    def move_to_the_right(self):
        """Move the charet to the right."""
        if self._charet_index < len(self._text):
            self._charet_index += 1

    def move_to_the_left(self):
        """Move the charet to the left."""
        if self._charet_index > 0:
            self._charet_index -= 1
