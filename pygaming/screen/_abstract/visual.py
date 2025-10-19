"""The visual module define the Visual class, a base class for everything that is displayed on the screen."""
from abc import ABC, abstractmethod
from pygame import Surface
from ..states import WidgetStates

class Visual(ABC):
    """The Visual class is the most abstract class representing anything on the screen."""
    
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._last_surface: Surface | None = None
        self._surface_changed = True
        self.state = WidgetStates.NORMAL # default value for everything on screen

    @property
    @abstractmethod
    def width(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def height(self):
        raise NotImplementedError()

    @property
    def size(self):
        return self.width, self.height

    def notify_change(self):
        """Notify a change in the visual."""
        self._surface_changed = True

    def update(self, dt):
        pass

    def loop(self, dt: int):
        self.update(dt)
    
    def begin(self, **kwargs):
        self.start(**kwargs)

    def finish(self):
        self.end()
    
    def start(self, **kwargs):
        pass

    def end(self):
        pass

    def get_surface(self) -> Surface:
        """Return the surface to be displayed."""
        if self._surface_changed or self._last_surface is None:
            self._surface_changed = False
            self._last_surface = self.make_surface()
        return self._last_surface

    @abstractmethod
    def make_surface(self) -> Surface:
        """Build the surface to be displayed."""
        raise NotImplementedError()
