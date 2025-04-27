"""The label module contains the Label Element used to display text."""
import pygame
from .._abstract import Textual
from ..hover import Hoverable
from ..frame import Frame
from ..anchors import CENTER, AnchorLike, Anchor
from ...color import Color
from ..art import Art
from ...database import TextFormatter
from ..hover import Cursor, Tooltip

class Label(Textual, Hoverable):
    """A Label is an element used to display text as a unjustified lines."""

    def __init__(
        self,
        master: Frame,
        background: Art,
        font: str,
        font_color: Color,
        localization_or_text: str | TextFormatter,
        tooltip: Tooltip = None,
        cursor: Cursor = None,
        justify: AnchorLike = CENTER,
        blinking_period: int = None,
        wrap: bool = False
    ) -> None:
        """
        Create the label
        Params:
        - master: Frame. The Frame in which the Label is placed.
        - background: A SurfaceLike object beiing the background of the text.
        - font: Font, the font to be used to display the text.
        - localization_or_text: The text, localization or TextFormatter to be displayed, can be modify with set_localization_or_text(new_text).
        - justify: the position of the text in the label, should be an anchor (i.e a tuple[x, y] with 0 <= x, y <= 1, or an Anchor2D from pygaming.anchor)
        - blinking_period: int [ms]. If an integer is specified, the text will blink with the given period.
        """
        super().__init__(
            master=master,
            art=background,
            tooltip=tooltip,
            cursor=cursor,
            font=font,
            color=font_color,
            text_or_loc=localization_or_text,
            jusitfy=justify,
            wrap=wrap
        )
        self.justify = Anchor(justify)
        self._blinking_period = blinking_period
        self._time_since_last_blink = 0
        self._show_text = True

    def set_localization_or_text(self, localization_or_text: str):
        """Set the label text to a new value."""
        if not isinstance(localization_or_text, (str, TextFormatter)):
            self.master.game.logger.write({"LabelError" : str(localization_or_text)}, True)
            localization_or_text = str(localization_or_text)
        elif self.text != localization_or_text:
            self.text = localization_or_text
            self.notify_change()

    def update(self, loop_duration: int):
        """Update the blinking of the text."""
        if self._blinking_period is not None:
            self._time_since_last_blink += loop_duration
            if self._time_since_last_blink > self._blinking_period//2:
                self._show_text = not self._show_text
                self._time_since_last_blink = 0
                self.notify_change()

    def _render_text(self):
        return self._fonts.render(
            self.game.typewriter,
            self.state,
            self.text,
            None,
            self.justify,
            True,
            self.wrap,
            self.width
        )

    def make_surface(self) -> pygame.Surface:
        """Return the surface of the Label."""
        bg = self._arts.get(self.state, **self.game.settings).copy()
        if self._show_text:
            rendered_text = self._render_text()
            text_width, text_height = rendered_text.get_size()
            just_x = self.justify[0]*(bg.get_width() - text_width)
            just_y = self.justify[1]*(bg.get_height() - text_height)
            bg.blit(rendered_text, (just_x, just_y))
        return bg

class Paragraph(Label):
    """A Paragraph is used to display a piece of a text as a justified paragraph."""

    def _render_text(self):
        font, color = self._fonts.get(self.state)
        return self.game.typewriter.render_paragraphs(font, self.text, color, self._arts.get(self.state), None)
