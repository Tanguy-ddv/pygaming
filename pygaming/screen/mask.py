from pygame import Surface, surfarray as sa
import numpy as np
import cv2
from abc import ABC, abstractmethod
from ..error import PygamingException

# Mask effects
ALPHA = 'alpha'
DARKEN = 'darken'
LIGHTEN = 'lighten'
SATURATE = 'saturate'
DESATURATE = 'desaturate'

_EFFECT_LIST = [ALPHA, DARKEN, LIGHTEN, SATURATE, DESATURATE]


class Mask(ABC):
    """Mask is an abstract class for all masks."""
    
    def __init__(self, width: int, height: int, effects: dict[str, float]) -> None:
        super().__init__()
        self._loaded = False
        self._alpha_matrix = None
        self._saturation_matrix = None
        self._light_matrix = None
        self._width = width
        self._height = height
        if DARKEN in effects.keys() and LIGHTEN in effects.keys():
            raise PygamingException("DARKEN and LIGHTEN cannot be effects of the same mask.")
        if SATURATE in effects.keys() and DESATURATE in effects.keys():
            raise PygamingException("SATURATE and DESATURATE cannot be effects of the same mask.")
        if any(key not in _EFFECT_LIST for key in effects.keys()):
            raise PygamingException(f"Invalid keys for mask effects, key allowed are pygaming.ALPHA, pygaming.LIGHTEN, pygaming.DARKEN, pygaming.SATURATE, pygaming.DESATURATE")

        self._effects = effects
    
    @abstractmethod
    def _load(self):
        raise NotImplementedError()
    
    def load(self):
        self._load()
        self._loaded = True

    def apply(self, surface: Surface):
        if not self._loaded:
            self.load()
        
        if surface.get_size() != (self._width, self._height):
            raise PygamingException("The size of the mask do not match the size of the art.")

        if ALPHA in self._effects:
            surf_alpha = sa.array_alpha(surface)
            surf_alpha[:] = np.astype(np.clip(surf_alpha*self._alpha_matrix/255, 0, 255), surf_alpha.dtype)

        if any(effect in self._effects for effect in _EFFECT_LIST[1:]):
            rgb_array = sa.pixels3d(surface)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)

            if DARKEN in self._effects:
                hls_array[:,:, 1] = hls_array[:,:, 1] * (1 - self._light_matrix)
            
            elif LIGHTEN in self._effects:
                hls_array[:,:, 1] = 255 - (255 - hls_array[:,:, 1])* (1 - self._light_matrix)

            if DESATURATE in self._effects:
                hls_array[:,:, 2] = hls_array[:,:, 2] * (1 - self._saturation_matrix)
            
            elif SATURATE in self._effects:
                hls_array[:,:, 2] = 255 - (255 - hls_array[:,:, 2])* (1 - self._saturation_matrix)

            rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[:]


    def unload(self):
        self._alpha_matrix = None
        self._saturation_matrix = None
        self._light_matrix = None
        self._loaded = False