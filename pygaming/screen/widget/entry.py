"""Then entry module contains the entry widget."""

from typing import Optional
from pygame import Cursor, Rect, Surface
from .widget import Widget
from ..element import SurfaceLike, TOP_LEFT
from ..colored_surfaces import ColoredRectangle
from ..frame import Frame
from ...font import Font

from ..label import TEXT_CENTERED, TEXT_RIGHT

class Entry(Widget):
    """The Entry widget is used to allow the user to add a textual input."""

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: SurfaceLike,
        normal_font: Font,
        focused_background: Optional[SurfaceLike] = None,
        focused_font: Optional[Font] = None,
        disabled_background: Optional[SurfaceLike] = None,
        disabled_font: Optional[Font] = None,
        initial_value: str = '',
        extra_characters: str = '',
        forbid_characters: str = '',
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Rect | None = None,
        layer: int = 0,
        hover_surface: Surface | None = None,
        hover_cursor: Cursor | None = None,
        continue_animation: bool = False,
        justify = TEXT_CENTERED,
        charet_frequency: int = 500,
        charet_width: int = 2,
        max_length: int = 10,
    ) -> None:
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

        self.max_length = max_length

        self._justify = justify
        self._charet_index = len(self._text)
        self._charet_frequency = charet_frequency
        self._charet = ColoredRectangle(self._focused_font.color, charet_width, self._focused_font.size('gh')[1])

        self._show_caret = True
        self._charet_delta = 0

    def set_text(self, new_text: str):
        """Set a new value for the entry."""
        self._text = str(new_text)

    def get(self):
        """Return the textual value currently entered."""
        return self._text

    def _get_disabled_surface(self) -> Surface:
        return self._get_surface(self.disabled_background.get(), self._disabled_font, False)

    def _get_focused_surface(self) -> Surface:
        return self._get_surface(self.focused_background.get(), self._disabled_font, self._show_caret)

    def _get_normal_surface(self) -> Surface:
        return self._get_surface(self.normal_background.get(), self._normal_font, False)

    def _get_surface(self, background: Surface, font: Font, charet: bool):
        rendered_text = font.render(self._text)
        text_width, text_height = rendered_text.get_size()
        y = (self._active_area.height - text_height)//2 + self._active_area.top
        if self._justify == TEXT_CENTERED:
            x = (self._active_area.width - text_width)//2 + self._active_area.left
        elif self._justify == TEXT_RIGHT:
            x = self._active_area.right - text_width
        else:
            x = self._active_area.left
        background.blit(rendered_text, (x,y))
        if charet:
            charet_x = x + font.size(self._text[:self._charet_index])[0]
            background.blit(self._charet, (charet_x, y))
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
            if self.game.keyboard.get_actions_down()['left']:
                self.move_to_the_left()
            if self.game.keyboard.get_actions_down()['right']:
                self.move_to_the_right()

            if self.game.keyboard.get_actions_down()['backspace']:
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
