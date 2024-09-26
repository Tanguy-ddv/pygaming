"""The button module contains buttons. They are widgets used to get a user click."""

from typing import Optional, Callable, Any
from pygame import Cursor, Rect, Surface
from ..frame import Frame
from ..element import TOP_LEFT
from ..element import SurfaceLike
from .widget import Widget, make_background

class Button(Widget):
    """A Button is a basic widget used to get a player click."""

    def __init__(
        self,
        master: Frame,
        x: int,
        y: int,
        normal_background: SurfaceLike,
        active_background: Optional[SurfaceLike] = None,
        focused_background: Optional[SurfaceLike] = None,
        disabled_background: Optional[SurfaceLike] = None,
        anchor: tuple[float | int, float | int] = TOP_LEFT,
        active_area: Optional[Rect] = None,
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
        self.active_background = make_background(active_background, self.normal_background)
        self._is_clicked = False
        self._command = command

    def get(self):
        """Return true if the button is clicked, false otherwise."""
        return self._is_clicked

    def _get_disabled_surface(self) -> Surface:
        return self.disabled_background.get()

    def _get_normal_surface(self) -> Surface:
        return self.normal_background.get()

    def _get_focused_surface(self) -> Surface:
        if self._is_clicked:
            return self.active_background.get()
        return self.focused_background.get()

    def update(self, loop_duration: int):
        """Update the widget."""

        ck1 = self.game.mouse.get_click(1)

        if (
            (   # This means the user is pressing 'return' while the button is focused
                self.focused
                and self.game.keyboard.get_actions_press()['return']
            )
            or ( # This means the user is clicking on the button
                ck1 is not None
                and self._absolute_active_area.collidepoint(ck1.x, ck1.y)
                and self._absolute_active_area.collidepoint(ck1.start_x, ck1.start_y)
            )
        ):
            # We verify if the user just clicked or if it is a long click.
            if not self._is_clicked:
                self._command()

            self._is_clicked = True

        else:
            self._is_clicked = False
