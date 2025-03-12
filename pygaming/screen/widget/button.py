"""The button module contains buttons. They are widgets used to get a user click."""

from typing import Optional, Callable, Any
from pygame import Surface
from ..frame import Frame
from ..anchors import TOP_LEFT, CENTER, Anchor
from .widget import Widget
from ..art import Art
from ...color import Color
from ...database import TextFormatter
from ...cursor import Cursor
from ..tooltip import Tooltip
from ..hitbox import Hitbox

class Button(Widget):
    """A Button is a basic widget used to get a player click."""

    def __init__(
        self,
        master: Frame,
        normal_background: Art,
        active_background: Optional[Art] = None,
        focused_background: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        hovered_background: Optional[Art] = None,
        active_area: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        on_click_command: Optional[Callable[[],Any]] = None,
        on_unclick_command: Optional[Callable[[],Any]] = None,
        update_if_invisible: bool = False
    ) -> None:
        """
        A Button is basic widget used to get a player click.

        Params:
        ---

        - master: Frame. The Frame in which this widget is placed.
        - normal_background: AnimatedSurface | Surface: The surface used as the background of the button when it is neither focused nor disabled.
        - active_background: AnimatedSurface | Surface: The surface used as the background of the button when it is clicked.
        - focused_background: AnimatedSurface | Surface: The surface used as the background of the button when it is focused.
        - disabled_background: AnimatedSurface | Surface: The surface used as the background of the button when it is disabled.
        - active_area: Rect. The Rectangle in the bacground that represent the active part of the button. if None, then it is the whole background.
        - tooltip: Tooltip, The tooltip to show when the button is hovered.
        - cursor: Cursor The cursor of the mouse to use when the widget is hovered
        - continue_animation: bool, If False, swapping state (normal, focused, disabled) restart the animations of the animated background.
        - on_click_command: a function to be called every time the button is clicked
        - on_unclick_command: a function to be call every time the button is unclicked
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
        self.active_background = active_background if active_background else normal_background
        self._is_clicked = False
        self._on_click_command = on_click_command
        self._on_unclick_command = on_unclick_command

    def get(self):
        """Return true if the button is clicked, false otherwise."""
        return self._is_clicked

    def _make_disabled_surface(self) -> Surface:
        return self.disabled_background.get(**self.game.settings, match=self.background if self._continue_animation else None)

    def _make_normal_surface(self) -> Surface:
        return self.normal_background.get(**self.game.settings, match=None)

    def _make_focused_surface(self) -> Surface:
        return self.focused_background.get(**self.game.settings, match=self.background if self._continue_animation else None)

    def _make_active_surface(self) -> Surface:
        return self.active_background.get(**self.game.settings, match=self.background if self._continue_animation else None)

    def _make_hovered_surface(self) -> Surface:
        return self.hovered_background.get(**self.game.settings, match=self.background if self._continue_animation else None)

    def make_surface(self):
        """Return the surface of the widget."""
        if self.disabled:
            return self._make_disabled_surface()
        elif self.focused:
            return self._make_focused_surface()
        elif self._hovered:
            return self._make_hovered_surface()
        elif self._is_clicked:
            return self._make_active_surface()
        else:
            return self._make_normal_surface()

    def loop(self, loop_duration: int):
        """Call this method every loop iteration."""
        if (self.on_master and self.is_visible()) or self._update_if_invisible:
            if not self._continue_animation:
                if self.disabled:
                    has_changed = self.disabled_background.update(loop_duration)
                elif self.focused:
                    has_changed = self.focused_background.update(loop_duration)
                elif self._hovered:
                    has_changed = self.hovered_background.update(loop_duration)
                elif self._is_clicked:
                    has_changed = self.active_background.update(loop_duration)
                else:
                    has_changed = self.normal_background.update(loop_duration)
                if has_changed:
                    self.notify_change()
            else:
                has_changed = self.normal_background.update(loop_duration)
                if has_changed:
                    self.notify_change()
            if self.is_visible():
                self.update(loop_duration)

    def switch_background(self):
        """Switch to the disabled, focused or normal background."""
        if not self._continue_animation:
            if self.disabled:
                self.active_background.reset()
                self.focused_background.reset()
                self.normal_background.reset()
                self.hovered_background.reset()
            elif self.focused:
                self.active_background.reset()
                self.normal_background.reset()
                self.disabled_background.reset()
                self.hovered_background.reset()
            elif self._hovered:
                self.active_background.reset()
                self.normal_background.reset()
                self.disabled_background.reset()
                self.focused_background.reset()
            elif self._is_clicked:
                self.normal_background.reset()
                self.disabled_background.reset()
                self.focused_background.reset()
                self.hovered_background.reset()
            else:
                self.active_background.reset()
                self.disabled_background.reset()
                self.focused_background.reset()
                self.hovered_background.reset()                

        self.notify_change()

    def start(self):
        """Execute this method at the beginning of the phase, load the arts that are set to force_load."""
        self.normal_background.start(**self.game.settings)
        self.focused_background.start(**self.game.settings)
        self.disabled_background.start(**self.game.settings)
        self.hovered_background.start(**self.game.settings)
        self.active_background.start(**self.game.settings)

    def end(self):
        """Execute this method at the end of the phase, unload all the arts."""
        self.normal_background.end()
        self.focused_background.end()
        self.disabled_background.end()
        self.hovered_background.end()
        self.active_background.end()

    def update(self, loop_duration: int):
        """Update the button every loop iteration if it is visible."""
        if not self.disabled:
            ck1 = self.game.mouse.get_click(1)

            if (
                (   # This means the user is pressing 'return' while the button is focused
                    self.focused
                    and self.game.keyboard.actions_down['return']
                )
                or ( # This means the user is clicking on the button
                    self.is_contact(ck1)
                    and self.is_contact((ck1.start_x, ck1.start_y)))
            ):
                # We verify if the user just clicked or if it is a long click.
                if not self._is_clicked:
                    self.notify_change()
                    if self._on_click_command is not None:
                        self._on_click_command()
                else:
                    self.notify_change()

                self._is_clicked = True

            else:
                if self._is_clicked:
                    self.notify_change()
                    if self._on_unclick_command is not None:
                        self._on_unclick_command()
                self._is_clicked = False

class TextButton(Button):
    """
    A Button is a basic widget used to get a player click.
    A text is displayed on this button.
    """

    def __init__(
        self,
        master: Frame,
        normal_background: Art,
        normal_font : str,
        normal_font_color: Color,
        localization_or_text: str | TextFormatter,
        active_background: Optional[Art] = None,
        active_font: Optional[str] = None,
        active_font_color: Optional[Color] = None,
        focused_background: Optional[Art] = None,
        focused_font: Optional[str] = None,
        focused_font_color: Optional[Color] = None,
        disabled_background: Optional[Art] = None,
        disabled_font: Optional[str] = None,
        disabled_font_color: Optional[Color] = None,
        hovered_background: Optional[str] = None,
        hovered_font: Optional[str] = None,
        hovered_font_color: Optional[Color] = None,
        active_area: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        on_click_command: Optional[Callable[[],Any]] = None,
        on_unclick_command: Optional[Callable[[],Any]] = None,
        jusitfy: Anchor = CENTER,
        update_if_invisible: bool = False
    ) -> None:
        super().__init__(
            master,
            normal_background,
            active_background,
            focused_background,
            disabled_background,
            hovered_background,
            active_area,
            tooltip,
            cursor,
            continue_animation,
            on_click_command,
            on_unclick_command,
            update_if_invisible
        )
        self.text = localization_or_text
        self.justify = jusitfy

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
        if active_font is None:
            active_font = normal_font
        self._active_font = active_font

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
        if active_font_color is None:
            active_font_color = normal_font_color
        self._active_font_color = active_font_color

    def make_surface(self):
        bg = super().make_surface()
        if self.disabled:
            rendered_text = self.game.typewriter.render(self._disabled_font, self.text, self._disabled_font_color, None, self.justify)
        elif self.focused:
            rendered_text = self.game.typewriter.render(self._focused_font, self.text, self._focused_font_color, None, self.justify)
        elif self._hovered:
            rendered_text = self.game.typewriter.render(self._hovered_font, self.text, self._hovered_font_color, None, self.justify)
        elif self._is_clicked:
            rendered_text = self.game.typewriter.render(self._active_font, self.text, self._active_font_color, None, self.justify)
        else:
            rendered_text = self.game.typewriter.render(self._normal_font, self.text, self._normal_font_color, None, self.justify)

        text_width, text_height = rendered_text.get_size()
        just_x = self.justify[0]*(bg.get_width() - text_width)
        just_y = self.justify[1]*(bg.get_height() - text_height)
        bg.blit(rendered_text, (just_x, just_y))
        return bg

    def set_localization_or_text(self, localization_or_text: str):
        """Set the button text to a new value."""
        if self.text != localization_or_text:
            self.text = str(localization_or_text)
            self.notify_change()
