"""The art class is the base for all the surfaces and animated surfaces of the game."""
from abc import ABC, abstractmethod
from pygame import Surface, image, surfarray as sa
from PIL import Image
from ...error import PygamingException
from ..window import Window
from ..anchors import TOP_LEFT
from ...settings import Settings
from ...file import get_file
from .transformation import Transformation

class Art(ABC):
    """The art class is the base for all the surfaces and animated surfaces of the game."""

    def __init__(self, transformation: Transformation = None, force_load_on_start: bool = False, permanent: bool = False) -> None:
        super().__init__()
        self.surfaces: tuple[Surface] = ()
        self.durations: tuple[int] = ()
        self.introduction = 0
        self._loaded = False

        self._time_since_last_change = 0
        self._index = 0

        self._height = -1
        self._width = -1
        self._on_loading_transformation = transformation

        self._force_load_on_start = force_load_on_start
        self._permanent = permanent
        self._copies: list[Art] = []
    
    def set_load_on_start(self):
        self._force_load_on_start = True

    def start(self, settings: Settings):
        """Call this method at the start of the phase."""
        if self._force_load_on_start and not self._loaded:
            self.load(settings)

    def _find_initial_dimension(self):
        if self._on_loading_transformation:
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
        """Return the size of the art."""
        return (self.width, self._height)
    
    @property
    def height(self):
        """Return the height of the art."""
        return self._height

    @property
    def width(self):
        """Return the width of the art."""
        return self._width
    
    @property
    def is_loaded(self):
        """Return true if the art is loaded"""
        return self._loaded

    @property
    def duration(self):
        """Return the durations of the frames in the art."""
        if len(self.durations) > 1:
            return sum(self.durations)
        return 0

    @abstractmethod
    def _load(self, settings: Settings):
        raise NotImplementedError()

    @property
    def index(self):
        """Return the current index of the frame displayed."""
        return self._index

    def unload(self):
        """Unload the surfaces."""
        if not self._permanent:
            self.surfaces = ()
            self.durations = ()
            self._loaded = False

    def load(self, settings: Settings):
        """Load the art at the beginning of the phase"""
        self._time_since_last_change = 0
        self._index = 0
        if not self._loaded:
            self._load(settings)
            self._verify_sizes()
            self._loaded = True
            if not self._on_loading_transformation is None:
                self.transform(self._on_loading_transformation, settings)

        for copy in self._copies:
            if not copy.is_loaded:
                copy.load(settings)

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
                    self._index = self.introduction
                return True
            return False
        return False

    def reset(self):
        """Reset the animation."""
        self._index = 0
        self._time_since_last_change = 0

    def get(self, settings: Settings, match: 'Art' = None):
        """
        Return the current Frame.
        
        - match: Art, if not None, the index will match the index of the other art to match, otherwise, use its own index
        """
        index = self._index if match is None else match.index
        if not self._loaded:
            self.load(settings)
        return self.surfaces[index].copy()

    def transform(self, transformation: Transformation, settings: Settings = None):
        """Apply a transformation"""
        if settings is None:
            antialias = False
        else:
            antialias = settings.antialias
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
                self.introduction,
                self._index,
                self._width,
                self._height,
                antialias
            )
        else:
            raise PygamingException("A transformation have be called on an unloaded Art, please use the art's constructor to transform the initial art.")

    def copy(self, additional_transformation: Transformation = None) -> '_ArtFromCopy':
        """
        Return an independant copy of the art.
        
        If force_load_on_start is set to True, the copy will be loaded at the start of the phase. Set it to true if 
        """
        copy = _ArtFromCopy(self, additional_transformation)
        self._copies.append(copy)
        return copy

    def to_window(self, x: int, y: int, anchor: tuple[float, float] = TOP_LEFT) -> Window:
        """Create a window without masked based on this art."""
        return Window(x, y, self.width, self.height, anchor)

    def save(self, path: str, index: int = None):
        """Save the art as a gif or as an image."""
        path = get_file('images', path)
        if len(self.surfaces) == 1:
            image.save(self.surfaces[0], path)
        elif not index is None:
            image.save(self.surfaces[index], path)
        else:
            pil_images = [Image.fromarray(sa.array3d(surf)) for surf in self.surfaces]
            pil_images[0].save(path, format='GIF', save_all=True, append_images = pil_images[1:], duration=self.durations)

class _ArtFromCopy(Art):

    def __init__(self, original: Art, additional_transformation: Transformation, permanent: bool = False):
        super().__init__(additional_transformation, original._force_load_on_start, permanent)
        # The on load transformation has been removed because the transformation are executed during the loading of the original
        self._original = original
        self._height = self._original.height
        self._width = self._original.width
        self._find_initial_dimension()

    def _load(self, settings: Settings):
        if not self._original.is_loaded:
            self._original.load(settings)

        self.surfaces = tuple(surf.copy() for surf in self._original.surfaces)
        self.durations = self._original.durations
        self.introduction = self._original.introduction

