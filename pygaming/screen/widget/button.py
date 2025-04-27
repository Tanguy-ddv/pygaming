"""The button module contains buttons. They are widgets used to get a user click."""

from typing import Optional, Callable, Any
from ..frame import Frame
from ..anchors import CENTER, AnchorLike
from ..states import WidgetStates
from .widget import Widget, TextualWidget
from ..art import Art
from ...color import Color
from ...database import TextFormatter
from ..hover import Tooltip, Cursor
from ..hitbox import Hitbox

class _Button(Widget):
    """Base class for buttons."""

    def __init__(
        self,
        master: Frame,
        art: Art,
        active_background: Optional[Art] = None,
        focused_art: Optional[Art] = None,
        disabled_art: Optional[Art] = None,
        hovered_art: Optional[Art] = None,
        hitbox: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        on_click_command: Optional[Callable[[],Any]] = None,
        on_unclick_command: Optional[Callable[[],Any]] = None,
        update_if_invisible: bool = False,
        **kwargs
    ) -> None:
        
        super().__init__(
            master,
            art=art,
            focused_art=focused_art,
            disabled_art=disabled_art,
            hovered_art=hovered_art,
            hitbox=hitbox,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            **kwargs
        )
        self._arts.add(WidgetStates.ACTIVE, active_background)
        self._on_click_command = on_click_command
        self._on_unclick_command = on_unclick_command

    def get(self):
        """Return true if the button is clicked, false otherwise."""
        return self.state == WidgetStates.ACTIVE

    def update(self, dt: int):
        """Update the button every loop iteration if it is visible."""
        if not self.state == WidgetStates.DISABLED:
            ck1 = self.game.mouse.get_click(1)

            if (
                (   # This means the user is pressing 'return' while the button is focused
                    self.state == WidgetStates.FOCUSED
                    and self.game.keyboard.actions_down['return']
                )
                or ( # This means the user is clicking on the button
                    self.is_contact(ck1)
                    and self.is_contact((ck1.start_x, ck1.start_y)))
            ):
                # We verify if the user just clicked or if it is a long click.
                if not self.state == WidgetStates.ACTIVE:
                    self.notify_change()
                    if self._on_click_command is not None:
                        self._on_click_command()

                    self._previous_state = self.state
                    self.state = WidgetStates.ACTIVE

            else:
                if self.state == WidgetStates.ACTIVE:
                    self.notify_change()
                    if self._on_unclick_command is not None:
                        self._on_unclick_command()
                    self.state = self._previous_state


class Button(_Button):
    """A Button is a basic widget used to get a player click."""

    def __init__(
        self,
        master: Frame,
        normal_background: Art,
        active_background: Optional[Art] = None,
        focused_background: Optional[Art] = None,
        disabled_background: Optional[Art] = None,
        hovered_background: Optional[Art] = None,
        hitbox: Optional[Hitbox] = None,
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
            art=normal_background,
            focused_art=focused_background,
            disabled_art=disabled_background,
            hovered_art=hovered_background,
            active_background=active_background,
            hitbox=hitbox,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            on_click_command=on_click_command,
            on_unclick_command=on_unclick_command,
        )

class TextButton(_Button, TextualWidget):
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
        hitbox: Optional[Hitbox] = None,
        tooltip: Optional[Tooltip] = None,
        cursor: Cursor | None = None,
        continue_animation: bool = False,
        on_click_command: Optional[Callable[[],Any]] = None,
        on_unclick_command: Optional[Callable[[],Any]] = None,
        justify: AnchorLike = CENTER,
        update_if_invisible: bool = False
    ) -> None:
        
        super().__init__(
            master=master,
            art=normal_background,
            focused_art=focused_background,
            disabled_art=disabled_background,
            hovered_art=hovered_background,
            active_background=active_background,
            hitbox=hitbox,
            tooltip=tooltip,
            cursor=cursor,
            continue_animation=continue_animation,
            update_if_invisible=update_if_invisible,
            font=normal_font,
            color=normal_font_color,
            text_or_loc=localization_or_text,
            focused_font=focused_font,
            focused_font_color=focused_font_color,
            disabled_font=disabled_font,
            disabled_font_color=disabled_font_color,
            hovered_font=hovered_font,
            hovered_font_color=hovered_font_color,
            justify=justify,
            on_click_command=on_click_command,
            on_unclick_command=on_unclick_command
        )
        self._fonts.add(WidgetStates.ACTIVE, active_font, active_font_color)

    def make_surface(self):
        return self._render_text_on_bg(self.game.settings, self.game.typewriter)
