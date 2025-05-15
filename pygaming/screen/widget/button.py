"""The button module contains buttons. They are widgets used to get a user click."""

from typing import Optional, Callable, Any, TypeVar, List
from ordered_set import OrderedSet
from ..frame import Frame
from ..anchors import CENTER, AnchorLike
from ..states import WidgetStates
from .widget import Widget, TextualWidget, CompositeWidget
from ..art import Art
from ...color import Color
from ...database import TextFormatter
from ..hover import Tooltip, Cursor
from ..hitbox import Hitbox
from ...error import PygamingException

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
        cursor: Optional[Cursor] = None,
        on_click_command: Optional[Callable[[], Any]] = None,
        on_unclick_command: Optional[Callable[[], Any]] = None,
        continue_animation: bool = False,
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
        on_click_command: Optional[Callable[[],Any]] = None,
        on_unclick_command: Optional[Callable[[],Any]] = None,
        justify: AnchorLike = CENTER,
        continue_animation: bool = False,
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

_T = TypeVar("T")
_ListOrObject = _T | List[_T]

def _make_list(loo: _ListOrObject[_T], expected_length: int) -> List[_T]:
    if isinstance(loo, List):
        if len(loo) != expected_length:
            raise PygamingException(f"{loo} should have a length of {expected_length}, but got {len(loo)}")
        return loo
    return [loo]*expected_length

class _MultiStateButton(CompositeWidget):

    def __init__(self, master: Frame, size: tuple[int, int], update_if_invisible: bool = True, reset_on_start: bool = True, **kwargs):
        super().__init__(master, size, update_if_invisible, **kwargs)
        self.__reset_on_start = reset_on_start
        self.__current_button_idx = 0
        self.focusable_children[0].show()
        self.set_link_focus(self.focusable_children[0])

    def begin(self):
        if self.__reset_on_start:
            self._linked_focus_widget.hide()
            self.__current_button_idx = 0
            current_button = self.focusable_children[self.__current_button_idx]
            current_button.show()
            self.set_link_focus(current_button)
        super().begin()

    def _next(self):
        self.__current_button_idx += 1
        self.__current_button_idx %= len(self.focusable_children)
        self._linked_focus_widget.hide()
        current_button = self.focusable_children[self.__current_button_idx]
        current_button.show()
        self.set_link_focus(current_button)
        self.notify_change()

class MultiStateButton(_MultiStateButton):

    def __init__(
        self,
        master: Frame,
        normal_background: List[Art],
        active_background: _ListOrObject[Optional[Art]] = None,
        focused_background: _ListOrObject[Optional[Art]] = None,
        disabled_background: _ListOrObject[Optional[Art]] = None,
        hovered_background: _ListOrObject[Optional[Art]] = None,
        hitbox: _ListOrObject[Optional[Hitbox]] = None,
        tooltip: _ListOrObject[Optional[Tooltip]] = None,
        cursor: _ListOrObject[Optional[Cursor]] = None,
        on_click_command: _ListOrObject[Optional[Callable[[], Any]]] = None,
        on_unclick_command: _ListOrObject[Optional[Callable[[], Any]]] = None,
        continue_animation: bool = False,
        update_if_invisible: bool = False,
        reset_on_start: bool = True,
    ):
        self.focusable_children: OrderedSet[_Button]
        length = len(normal_background)
        for nbg, abg, fbg, dbg, hbg, hbx, tt, curs, oncc, onuc in zip(
            _make_list(normal_background, length),
            _make_list(active_background, length),
            _make_list(focused_background, length),
            _make_list(disabled_background, length),
            _make_list(hovered_background, length),
            _make_list(hitbox, length),
            _make_list(tooltip, length),
            _make_list(cursor, length),
            _make_list(on_click_command, length),
            _make_list(on_unclick_command, length)
        ):
            def new_on_unclick():
                if onuc is not None:
                    onuc()
                self._next()

            _b = _Button(
                self,
                nbg, abg, fbg, dbg, hbg, hbx, tt, curs,
                continue_animation, oncc, new_on_unclick, update_if_invisible
            )
            _b.place(0, 0)
            _b.hide()
        
        super().__init__(master, normal_background[0].size, update_if_invisible, reset_on_start)

class TextMultiStateButton(_MultiStateButton):

    def __init__(
        self,
        master: Frame,
        normal_background: List[Art],
        normal_font: _ListOrObject[str],
        normal_font_color: _ListOrObject[Color],
        localization_or_text: _ListOrObject[str | TextFormatter],
        active_background: _ListOrObject[Optional[Art]] = None,
        active_font: _ListOrObject[Optional[str]] = None,
        active_font_color: _ListOrObject[Optional[Color]] = None,
        focused_background: _ListOrObject[Optional[Art]] = None,
        focused_font: _ListOrObject[Optional[str]] = None,
        focused_font_color: _ListOrObject[Optional[Color]] = None,
        disabled_background: _ListOrObject[Optional[Art]] = None,
        disabled_font: _ListOrObject[Optional[str]] = None,
        disabled_font_color: _ListOrObject[Optional[Color]] = None,
        hovered_background: _ListOrObject[Optional[str]] = None,
        hovered_font: _ListOrObject[Optional[str]] = None,
        hovered_font_color: _ListOrObject[Optional[Color]] = None,
        hitbox: _ListOrObject[Optional[Hitbox]] = None,
        tooltip: _ListOrObject[Optional[Tooltip]] = None,
        cursor: _ListOrObject[Optional[Cursor]] = None,
        on_click_command: _ListOrObject[Optional[Callable[[], Any]]] = None,
        on_unclick_command: _ListOrObject[Optional[Callable[[], Any]]] = None,
        justify: _ListOrObject[AnchorLike] = CENTER,
        continue_animation: bool = False,
        update_if_invisible: bool = False,
        reset_on_start: bool = True,
    ):
        self.focusable_children: OrderedSet[_Button]
        length = len(normal_background)
        for nbg, nf, nfc, loc, abg, af, afc, fbg, ff, ffc, dbg, df, dfc, hbg, hf, hfc, hbx, tt, curs, oncc, onuc, just in zip(
            _make_list(normal_background, length),
            _make_list(normal_font, length),
            _make_list(normal_font_color, length),
            _make_list(localization_or_text, length),
            _make_list(active_background, length),
            _make_list(active_font, length),
            _make_list(active_font_color, length),
            _make_list(focused_background, length),
            _make_list(focused_font, length),
            _make_list(focused_font_color, length),
            _make_list(disabled_background, length),
            _make_list(disabled_font, length),
            _make_list(disabled_font_color, length),
            _make_list(hovered_background, length),
            _make_list(hovered_font, length),
            _make_list(hovered_font_color, length),
            _make_list(hitbox, length),
            _make_list(tooltip, length),
            _make_list(cursor, length),
            _make_list(on_click_command, length),
            _make_list(on_unclick_command, length),
            _make_list(justify, length)
        ):
            def new_on_unclick():
                if onuc is not None:
                    onuc()
                self._next()

            _b = TextButton(
                self,
                nbg, nf, nfc, loc, abg, af, afc,
                fbg, ff, ffc, dbg, df, dfc, hbg, hf, hfc, hbx, tt, curs,
                oncc, new_on_unclick, just, continue_animation, update_if_invisible
            )
            _b.place(0, 0)
            _b.hide()
        
        super().__init__(master, normal_background[0].size, update_if_invisible, reset_on_start)
