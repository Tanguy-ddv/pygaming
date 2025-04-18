"""The visual module define the Visual class, a base class for everything that is displayed on the screen."""
from abc import ABC, abstractmethod
from pygame import Surface

class Visual(ABC):
    """The Visual class is the most abstract class representing anything on the screen."""
    
    def __init__(self) -> None:
        super().__init__()
        self._last_surface: Surface | None = None
        self._surface_changed = True

    @property
    @abstractmethod
    def width(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def height(self):
        raise NotImplementedError

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
