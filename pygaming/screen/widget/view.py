"""The view module contains the View class which is used to have a view on a frame through a different camera."""
from pygame import Surface, transform
from ...error import PygamingException
from ..camera import Camera
from .._abstract import Placeable
from ..art import Art
from ..frame import Frame

class View(Placeable):

    def __init__(self, master: Frame, camera: Camera, target: Frame, foreground: Art | None = None, width: int = None, height: int = None, **kwargs):
        super().__init__(master, False, **kwargs)
        if master is target:
            raise PygamingException("A view cannot target its own master.")
        if width is None:
            if foreground is None:
                width = camera.width
            else:
                width = foreground.width

        self._width = width

        if height is None:
            if foreground is None:
                height = camera.height
            else:
                height = foreground.height

        self._height = height
        self.camera = camera
        self.target = target
        self.foreground = foreground

        target.views.add(self)

    def notify_change(self):
        """Notify a change in the visual."""
        self._surface_changed = True
        if self.is_visible():
            self.master.notify_change()
    
    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def loop(self, dt: int):
        super().loop(dt)
        if self.foreground is not None and self.is_visible():
            has_changed = self.foreground.update(dt)
            if has_changed:
                self.notify_change()

    def make_surface(self) -> Surface:
        view = self.camera.get_surface(self.target.get_surface(), self.master.game.settings)
        if view.get_size() != (self.width, self.height):
            view = transform.scale(view, (self.width, self.height))
        if self.foreground is not None:
            view.blit(self.foreground.get(None, **self.master.game.settings), (0, 0))
        return view
