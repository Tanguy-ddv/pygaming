"""The progess_bar module contains the ProgressBar."""
from pygame.transform import scale, smoothscale
from typing import Literal
from ZOCallable import ZOCallable, verify_ZOCallable
from ZOCallable.functions import linear
from pygame.surface import Surface as Surface
from ..element import Element
from ..frame import Frame
from ..anchors import Anchor
from ...color import Color
from ..art import Art, Rectangle
from ...database import TextFormatter
from ..tooltip import Tooltip
from ...cursor import Cursor

class ProgressBar(Element):

    def __init__(
        self,
        master: Frame,
        bar: Art,
        initial_value: float,
        background: Art = None,
        foreground: Art = None,
        extending_side: Literal[Anchor.TOP, Anchor.BOTTOM, Anchor.LEFT, Anchor.RIGHT] = Anchor.RIGHT,
        displaying: Literal['scaling', 'sliding', 'hiding', 'smooth_scaling'] = 'sliding',
        # rescale the bar, move the bar the opposite of the extending side, hide the extending side.
        transition_function: ZOCallable = linear,
        transition_duration: int = 300, # [ms]
        tooltip: Tooltip = None,
        cursor: Cursor = None,
    ):

        if background is None:
            background = Rectangle((0, 0, 0, 0), *bar.size)

        if foreground is None:
            foreground = Rectangle((0, 0, 0, 0), *bar.size)

        super().__init__(master, background, tooltip, cursor, False, False, None, False)

        self.foreground = foreground
        self.bar = bar
        self._value = max(min(initial_value, 1), 0)
        self._extending_side = extending_side
        self._displaying = displaying

        # Transition-related attributes
        verify_ZOCallable(transition_function)
        self._transition_func = transition_function
        self._transition_duration = transition_duration
        self._current_transition = None
        self._current_transition_delta = 0
        self._current_position = self._value

    def set_value(self, new_value: float):
        self._value = new_value
        self._current_transition = (self._current_position, self._value)

    def start(self):
        self.foreground.start(**self.game.settings)
        self.bar.start(**self.game.settings)

    def end(self):
        self.foreground.end()
        self.bar.end()

    def update(self, loop_duration):
        """Update the progress bar."""

        # Update arts.
        has_changed = self.bar.update(loop_duration) or self.foreground.update(loop_duration)
        if has_changed:
            self.notify_change()

        # Move the current_position
        if self._current_transition is not None:
            self.notify_change()
            if self._transition_duration > 0:
                self._current_transition_delta += loop_duration/self._transition_duration
            else:
                self._current_transition_delta = 1.01
            t = self._transition_func(self._current_transition_delta)
            self._current_position = self._current_transition[0]*(1-t) + t*self._current_transition[1]

            # If we finished the transition
            if self._current_transition_delta >= 1:
                self._current_transition_delta = 0
                self._current_transition = None
                self._current_position = self._value

    def make_surface(self) -> Surface:
        background = self.background.get(None, copy=True, **self.game.settings)
        foreground = self.foreground.get(None, copy=False, **self.game.settings)
        bar = self.bar.get(None, copy=False, **self.game.settings)
        # For each case, find the blitting coordinate and the perhaps transformed bar.
        if self._displaying == 'sliding':
            if self._extending_side == Anchor.TOP:
                pos = 0, int(background.get_height()*(1-self._current_position))
            elif self._extending_side == Anchor.BOTTOM:
                pos = 0, -int(background.get_height()*(1-self._current_position))
            elif self._extending_side == Anchor.LEFT:
                pos = int(background.get_width()*(1-self._current_position)), 0
            else:
                pos = -int(background.get_width()*(1-self._current_position)), 0

        elif self._displaying == 'scaling':
            if self._extending_side == Anchor.BOTTOM:
                pos = 0, 0
                bar = scale(bar, (bar.get_width(), int(background.get_height()*self._current_position)))
            elif self._extending_side == Anchor.TOP:
                pos = 0, int(background.get_height()*(1-self._current_position))
                bar = scale(bar, (bar.get_width(), int(background.get_height()*self._current_position)))
            elif self._extending_side == Anchor.LEFT:
                pos = int(background.get_width()*(1-self._current_position)), 0
                bar = scale(bar, (int(background.get_width()*self._current_position), bar.get_height()))
            else:
                pos = 0, 0
                bar = scale(bar, (int(background.get_width()*self._current_position), bar.get_height()))

        elif self._displaying == 'smooth_scaling':
            if self._extending_side == Anchor.BOTTOM:
                pos = 0, 0
                bar = smoothscale(bar, (bar.get_width(), int(background.get_height()*self._current_position)))
            elif self._extending_side == Anchor.TOP:
                pos = 0, int(background.get_height()*(1-self._current_position))
                bar = smoothscale(bar, (bar.get_width(), int(background.get_height()*self._current_position)))
            elif self._extending_side == Anchor.LEFT:
                pos = int(background.get_width()*(1-self._current_position)), 0
                bar = smoothscale(bar, (int(background.get_width()*self._current_position), bar.get_height()))
            else:
                pos = 0, 0
                bar = smoothscale(bar, (int(background.get_width()*self._current_position), bar.get_height()))

        else:
            if self._extending_side == Anchor.BOTTOM:
                pos = 0, 0
                bar = bar.subsurface((
                    0, 0 ,bar.get_width(), int(background.get_height()*self._current_position)
                ))
            elif self._extending_side == Anchor.TOP:
                pos = 0, int(background.get_height()*(1-self._current_position))
                bar = bar.subsurface((
                    0, int(background.get_height()*(1-self._current_position)),
                    bar.get_width(), int(background.get_height()*self._current_position)
                ))
            elif self._extending_side == Anchor.LEFT:
                pos = 0, 0
                bar = bar.subsurface((int(background.get_width()*(1-self._current_position)), 0, int(background.get_width()*self._current_position), bar.get_height()))
            else:
                pos = int(background.get_height()*(1-self._current_position)), 0
                bar = bar.subsurface(0, 0, int(background.get_width()*self._current_position), bar.get_height())
        
        # Draw the bar and the foreground on top of everything and return
        background.blit(bar, pos)
        background.blit(foreground, (0, 0))
        return background
