"""The child module defines the child class that are abstract visual objects with a master."""
from abc import abstractmethod
from typing import Self
from pygame import Rect, Surface
from .visual import Visual
from .master import Master

class Child(Visual):
    
    def __init__(self, master: Master, update_if_invisible: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.master = master
        self.master.add_child(self, False, False, False, False, False)
        self._visible = True
        self._update_if_invisible = update_if_invisible
        self.absolute_rect: Rect

    @abstractmethod
    def make_surface(self) -> Surface:
        raise NotImplementedError()

    def hide(self) -> Self:
        """Hide the object."""
        self._visible = False
        self.master._clear_cache()
        self.master.notify_change()
        return self

    def show(self) -> Self:
        """Show the object."""
        self._visible = True
        self.master._clear_cache()
        self.master.notify_change()
        return self

    def toggle_visibility(self) -> Self:
        """Toggle the object visibility."""
        self._visible = not self._visible
        self.master._clear_cache()
        self.master.notify_change()
        return self

    def get_visibility(self):
        return self._visible

    def is_visible(self):
        return self.get_visibility() and self.master.is_child_on_me(self)

    @property
    def game(self):
        """Return the game."""
        return self.master.game

    def notify_change(self):
        """Notify a change in the visual."""
        self._surface_changed = True
        if self.is_visible():
            self.master.notify_change()

    def loop(self, dt: int):
        if self.is_visible() or self._update_if_invisible:
            super().loop(dt)
