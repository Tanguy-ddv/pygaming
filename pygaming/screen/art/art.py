"""The art class is the base for all the surfaces and animated surfaces of the game."""
from abc import ABC, abstractmethod
from pygame import Surface

from ...error import PygamingException

class Art(ABC):
    """The art class is the base for all the surfaces and animated surfaces of the game."""

    def __init__(self, transformation = None, force_load_on_start: bool = False) -> None:
        super().__init__()
        self.surfaces: tuple[Surface] = ()
        self.durations: tuple[int] = ()
        self._introduction = 0
        self._loaded = False

        self._time_since_last_change = 0
        self._index = 0

        self._height = -1
        self._width = -1
        self._on_loading_transformation = transformation

        self._force_load_on_start = force_load_on_start
    
    def start(self):
        """Call this method at the start of the phase."""
        if self._force_load_on_start and not self._loaded:
            self.load()
    
    def _find_initial_dimension(self):
        if self._on_loading_transformation :
            self._width, self._height = self._on_loading_transformation.get_new_dimension(self._width, self._height)
    
    def _verify_sizes(self):
        """verify that all surfaces have the same sizes."""
        heights = [surf.get_height() for surf in self.surfaces]
        widths = [surf.get_width() for surf in self.surfaces]
        if len(set(heights)) != 1:
            raise PygamingException(f"All images of the art does not have the same height, got\n{heights}")
        if len(set(widths)) != 1:
            raise PygamingException(f"All images of the art does not have the same width, got\n{widths}")

    @property
    def size(self):
        return (self.width, self._height)
    
    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width
    
    @property
    def is_loaded(self):
        return self._loaded

    @property
    def loop_duration(self):
        if len(self.durations) > 1:
            return sum(self.durations)
        return 0

    @abstractmethod
    def _load(self):
        raise NotImplementedError()

    @property
    def index(self):
        return self._index

    def unload(self):
        """Unload the surfaces."""
        self.surfaces = ()
        self.durations = ()
        self._loaded = False

    def load(self):
        """Load the art at the beginning of the phase"""
        self._time_since_last_change = 0
        self._index = 0
        self._load()
        self._verify_sizes()
        self._loaded = True
        if self._on_loading_transformation is not None:
            self.transform(self._on_loading_transformation)

    def update(self, loop_duration: float) -> bool:
        """
        Update the instance animation.
        
        Return True if the index changed.
        """
        if len(self.surfaces) > 1:
            self._time_since_last_change += loop_duration
            if self._time_since_last_change >= self.durations[self._index]:
                self._time_since_last_change -= self.durations[self._index]
                self._index += 1
                if self._index == len(self.surfaces):
                    self._index = self._introduction
                return True
            return False
        else:
            return False
            
    def reset(self):
        """Reset the animation."""
        self._index = 0
        self._time_since_last_change = 0
    
    def get(self, match: 'Art' = None):
        """
        Return the current Frame.
        
        - match: Art, if not None, the index will match the index of the other art to match, otherwise, use its own index
        """
        index = self._index if match is None else match.index
        if not self._loaded:
            self.load()
        return self.surfaces[index].copy()

    def transform(self, transformation):
        """Apply a transformation"""
        if self._loaded:
            (   self.surfaces,
                self.durations,
                self.introduction,
                self._index,
                self._width,
                self._height
            ) = transformation.apply(
                self.surfaces,
                self.durations,
                self._introduction,
                self._index,
                self._width,
                self._height
            )
        else:
            raise PygamingException("A transformation have be called on an unload Art, please use the art's constructor to transform the initial art.")