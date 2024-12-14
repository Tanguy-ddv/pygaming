"""The button module contains buttons. They are widgets used to get a user click."""

from typing import Optional, Callable, Any
from pygame import Cursor, Rect, Surface
from ..frame import Frame
from ..anchors import TOP_LEFT, CENTER
from .widget import Widget
from ..art import Art
from ...color import Color
from ..mask import Mask

class Button(Widget):
    """A Button is a basic widget used to get a player click."""

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: Art,
        active_background: Optional[Art] = None,
        focused_background: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Optional[Mask] = None,
        layer: int = 0,
        hover_surface: Optional[Surface] = None,
        hover_cursor: Optional[Cursor] = None,
        continue_animation: bool = False,
        command: Optional[Callable[[],Any]] = None
    ) -> None:
        """
        A Button is basic widget used to get a player click.

        Params:
        ---

        - master: Frame. The Frame in which this widget is placed.
        - x: int, the coordinate of the anchor in the master Frame
        - y: int, the top coordinate of the anchor in the master Frame.
        - normal_background: AnimatedSurface | Surface: The surface used as the background of the button when it is neither focused nor disabled.
        - active_background: AnimatedSurface | Surface: The surface used as the background of the button when it is clicked.
        - focused_background: AnimatedSurface | Surface: The surface used as the background of the button when it is focused.
        - disabled_background: AnimatedSurface | Surface: The surface used as the background of the button when it is disabled.
        - anchor: tuple[float, float]. The point of the button that is placed at the coordinate (x,y).
          Use TOP_LEFT, TOP_RIGHT, CENTER, BOTTOM_LEFT or BOTTOM_RIGHT, or another personized tuple.
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the button. if None, then it is the whole background.
        - layer: int, the layer of the button in its master frame
        - hover_surface: Surface, The surface to show when the button is hovered.
        - hover_cursor: Cursor The cursor of the mouse to use when the widget is hovered
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - command: a function to be called every time the button is clicked        
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
        self.active_background = active_background if active_background else normal_background
        self._is_clicked = False
        self._command = command

    def get(self):
        """Return true if the button is clicked, false otherwise."""
        return self._is_clicked

    def _make_disabled_surface(self) -> Surface:
        return self.disabled_background.get(self.game.settings, self.surface if self._continue_animation else None)

    def _make_normal_surface(self) -> Surface:
        return self.normal_background.get(self.game.settings, self.surface if self._continue_animation else None)

    def _make_focused_surface(self) -> Surface:
        if self._is_clicked:
            return self.active_background.get(self.game.settings, self.surface if self._continue_animation else None)
        return self.focused_background.get(self.game.settings, self.surface if self._continue_animation else None)

    def update(self, loop_duration: int):
        """Update the widget."""

        ck1 = self.game.mouse.get_click(1)

        if (
            (   # This means the user is pressing 'return' while the button is focused
                self.focused
                and self.game.keyboard.actions_down['return']
            )
            or ( # This means the user is clicking on the button
                self.is_contact(ck1)
                and self.is_contact((ck1.start_x, ck1.start_y))
            )
        ):
            # We verify if the user just clicked or if it is a long click.
            if not self._is_clicked:
                self.notify_change()
                if self._command is not None:
                    self._command()
            else:
                self.notify_change()

            self._is_clicked = True

        else:
            if self._is_clicked:
                self.notify_change()
            self._is_clicked = False

class TextButton(Button):
    """
    A Button is a basic widget used to get a player click.
    A text is displayed on this button.
    """

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: Art,
        font : str,
        font_color: Color,
        localization_or_text: str,
        active_background: Optional[Art] = None,
        focused_background: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Rect | None = None,
        layer: int = 0,
        hover_surface: Surface | None = None,
        hover_cursor: Cursor | None = None,
        continue_animation: bool = False,
        command: Callable[[], Any] | None = None,
        jusitfy = CENTER
    ) -> None:
        super().__init__(
            master,
            x,
            y,
            normal_background,
            active_background,
            focused_background,
            disabled_background,
            anchor,
            active_area,
            layer,
            hover_surface,
            hover_cursor,
            continue_animation,
            command
        )
        self.font = font
        self.font_color = font_color
        self.text = localization_or_text
        self.justify = jusitfy

    def make_surface(self):
        bg = super().get_surface()
        rendered_text = self.game.typewriter.render(self.font, self.text, self.font_color, None)
        text_width, text_height = rendered_text.get_size()
        just_x = self.justify[0]*(bg.get_width() - text_width)
        just_y = self.justify[1]*(bg.get_height() - text_height)
        bg.blit(rendered_text, (just_x, just_y))
        return bg
