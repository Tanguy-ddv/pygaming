"""The art class is the base for all the surfaces and animated surfaces of the game."""
from abc import ABC, abstractmethod
from pygame import Surface, image, surfarray as sa
from PIL import Image

from ...error import PygamingException
from ..window import Window
from ..anchors import TOP_LEFT
from ...settings import Settings
from ...file import get_file

from .transformation import Transformation, Pipeline

class Art(ABC):
    """The art class is the base for all the surfaces and animated surfaces of the game."""

    def __init__(self, transformation = Transformation, force_load_on_start: bool = False) -> None:
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
        self._copies: list[Art] = []
    
    def start(self, settings: Settings):
        """Call this method at the start of the phase."""
        if self._force_load_on_start and not self._loaded:
            self.load(settings)
    
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

    def load(self, settings: Settings):
        """Load the art at the beginning of the phase"""
        self._time_since_last_change = 0
        self._index = 0
        self._load()
        self._verify_sizes()
        self._loaded = True
        if self._on_loading_transformation is not None:
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

    def transform(self, transformation: Transformation, settings: Settings):
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
                self.introduction,
                self._index,
                self._width,
                self._height,
                settings.antialias
            )
        else:
            raise PygamingException("A transformation have be called on an unloaded Art, please use the art's constructor to transform the initial art.")

    def copy(self) -> 'Art':
        """
        Return an independant copy of the art.
        
        If force_load_on_start is set to True, the copy will be loaded at the start of the phase. Set it to true if 
        """
        copy = _ArtFromCopy(self)
        self._copies.append(copy)
        return copy

    def to_window(self, x: int, y: int, anchor: tuple[float, float] = TOP_LEFT) -> Window:
        """Create a window without masked based on this art."""
        return Window(x, y, self.width, self.height, anchor)

    def save(self, path: str, index: int = None, permanent: bool = False):
        path = get_file('images', path, permanent)
        if len(self.surfaces) == 1:
            image.save(self.surfaces[0], path)
        elif not (index is None):
            image.save(self.surfaces[index], path)
        else:
            pil_images = [Image.fromarray(sa.array3d(surf)) for surf in self.surfaces]
            pil_images[0].save(path, format='GIF', save_all=True, append_images = pil_images[1:], duration=self.durations)

class _ArtFromCopy(Art):

    def __init__(self, original: Art):
        super().__init__(original._force_load_on_start)
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

    def add_on_load_transformation(self, *transformation: Transformation):
        """
        Add new transformation for a copy of an Art. This transformation will be apply at the loading of the copy of the art
        and will not transform the original. Note that calling this method would work only for copies. Note that calling this
        method after loading will not do anything. Please use the .transform() method in this case.
        """
        if self._on_loading_transformation: #The method can be used more than once
            self._on_loading_transformation = Pipeline(self._on_loading_transformation, *transformation)
        else: # At the creation of the copy, it does not have any on loeading transformation.
            self._on_loading_transformation = Pipeline(*transformation)
        self._find_initial_dimension()
    