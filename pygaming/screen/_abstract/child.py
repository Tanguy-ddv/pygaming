"""The child module defines the child class that are abstract visual objects with a master."""
from .visual import Visual
from .master import Master
from pygame import Rect

class Child(Visual):
    
    def __init__(self, master: Master, update_if_invisible: bool = False, add_to_master: bool = True) -> None:
        super().__init__()
        self.master = master
        if add_to_master:
            self.master.add_child(self)
        self._visible = True
        self._update_if_invisible = update_if_invisible
        self.absolute_rect: Rect

    def hide(self):
        self._visible = False

    def show(self):
        self._visible = True

    def toggle_visibility(self):
        self._visible = not self._visible

    def get_visibility(self):
        return self._visible

    def is_visible(self):
        return self.get_visibility() and self.master.is_child_on_me(self)

    def notify_change(self):
        """Notify a change in the visual."""
        self._surface_changed = True
        if self.is_visible():
            self.master.notify_change()

    def loop(self, dt: int):
        if self.is_visible() or self._update_if_invisible:
            self.update(dt)

    def start(self):
        pass

    def begin(self):
        self.start()

    def end(self):
        pass

    def finish(self):
        self.end()