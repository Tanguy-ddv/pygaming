from typing import Callable
from pygame import Surface, transform as tf, surfarray as sa
from ._transformation import Transformation
import numpy as np
import cv2
from ...mask import Mask

class SetAlpha(Transformation):
    """
    if alpha is specified, the SetAlpha transformation replace the alpha value of all the pixel by a new value.
    if mask is specified, the transformation replace the alpha value of all pixel by the value of the mask.
    Pixels that are transparent from the begining will not change.
    """

    def __init__(self, alpha: int = None, mask: Mask = None) -> None:
        super().__init__()
        if alpha is None and mask is None:
            raise ValueError("Both alpha and mask cannot be None.")
        self.alpha = alpha
        self.mask = mask

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        if self.mask is None:
            for surf in surfaces:
                surf.set_alpha(self.alpha)
        else:
            if not self.mask.is_loaded():
                self.mask.load()
            for surf in surfaces:
                alpha_array = sa.pixels_alpha(surf)
                alpha_array[:] = (1 - self.mask.matrix)*255
        
        return surfaces, durations, introduction, index, width, height

class GrayScale(Transformation):
    """
    The gray scale transformation turn the art into a black and white art.
    """

    def __init__(self) -> None:
        super().__init__()
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        graysurfeaces = tuple(tf.grayscale(surf) for surf in surfaces)
        return graysurfeaces, durations, introduction, index, width, height

class RBGMap(Transformation):
    """
    An RGBMap is a transformation applied directly on the pixel of the surfaces. The alpha value is not taken into account.
    the function must be vectorized. (check numpy.vectorize)
    """

    def __init__(self, function: Callable[[int, int, int], tuple[int, int, int]], mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.function = function
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.apply_along_axis(self.function, 2, rgb_array)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = np.apply_along_axis(self.function, 2, rgb_array)[self.mask.matrix > self.mask_threshold]

        return surfaces, durations, introduction, index, width, height
    
class RGBAMap(Transformation):
    """
    An RGBAMap is a transformation applied directly on the pixel of the surfaces. The alpha value is taken into account.
    the function must be vectorized. (check numpy.vectorize)
    """

    def __init__(self, function: Callable[[int, int, int, int], tuple[int, int, int, int]], mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.function = function
        self.mask = mask
        self.mask_threshold = mask_threshold

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):

        for surf in surfaces:

            rgb_array = sa.pixels3d(surf)
            alpha_array = sa.pixels_alpha(surf)

            r, g, b = rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2]
            new_r, new_g, new_b, new_a = self.function(r, g, b, alpha_array)
            if self.mask is None:
                rgb_array[:, :, 0] = new_r
                rgb_array[:, :, 1] = new_g
                rgb_array[:, :, 2] = new_b
                alpha_array[:] = new_a
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[:, :, 0][self.mask.matrix > self.mask_threshold] = new_r[self.mask.matrix > self.mask_threshold]
                rgb_array[:, :, 1][self.mask.matrix > self.mask_threshold] = new_g[self.mask.matrix > self.mask_threshold]
                rgb_array[:, :, 2][self.mask.matrix > self.mask_threshold] = new_b[self.mask.matrix > self.mask_threshold]
                alpha_array[self.mask > self.mask_threshold] = new_a[self.mask > self.mask_threshold]

        return surfaces, durations, introduction, index, width, height

class Saturate(Transformation):
    """Saturate the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.factor = factor
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)
            hls_array[:,:, 2] = 255 - (255 - hls_array[:,:, 2])* (1 - self.factor)
            if self.mask is None:
                rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[:][self.mask.matrix > self.mask_threshold]

        return surfaces, durations, introduction, index, width, height

class Desaturate(Transformation):
    """Desaturate the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.factor = factor
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)
            hls_array[:,:, 2] = hls_array[:,:, 2] * (1 - self.factor)
            if self.mask is None:
                rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[self.mask.matrix > self.mask_threshold]
        return surfaces, durations, introduction, index, width, height

class Darken(Transformation):
    """Darken the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.factor = factor
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)
            hls_array[:,:, 1] = hls_array[:,:, 1] * (1 - self.factor)
            if self.mask is None:
                rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[self.mask.matrix > self.mask_threshold]
        return surfaces, durations, introduction, index, width, height

class Lighten(Transformation):
    """Lighten the art by a given factor."""

    def __init__(self, factor: float, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.factor = factor
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            hls_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HLS)
            hls_array[:,:, 1] = 255 - (255 - hls_array[:,:, 1])* (1 - self.factor)
            if self.mask is None:
                rgb_array[:] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = cv2.cvtColor(hls_array, cv2.COLOR_HLS2RGB)[self.mask.matrix > self.mask_threshold]
        return surfaces, durations, introduction, index, width, height

class Invert(Transformation):
    """Invert the color of the art."""

    def __init__(self, mask: Mask = None, mask_threshold: float = 0.99):
        super().__init__()
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = 255 - rgb_array
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = 255 - rgb_array[self.mask.matrix > self.mask_threshold]
        return surfaces, durations, introduction, index, width, height

class AdjustContrast(Transformation):
    """Change the contrast of an art. The constrast is a value between -255 and +255."""

    def __init__(self, contrast: int, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
        self.contrast = contrast
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip((self.factor * (rgb_array - 128) + 128).astype(int), 0, 255)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(
                    (self.factor * (rgb_array - 128) + 128).astype(int), 0, 255)[self.mask.matrix > self.mask_threshold]

        return surfaces, durations, introduction, index, width, height

class AdjustBrightness(Transformation):
    """Change the brightness of an art. The brightness is a value between -255 and +255."""

    def __init__(self, brightness: int, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.brightness = int(brightness)
        self.mask = mask
        self.mask_threshold = mask_threshold
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip(rgb_array + self.brightness, 0, 255)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(rgb_array + self.brightness, 0, 255)[self.mask.matrix > self.mask_threshold]
        return surfaces, durations, introduction, index, width, height

class Gamma(Transformation):
    """
    The gamma transformation is used to modify the brightness of the image.
    For 0 < gamma < 1, the dark pixels will be brighter and the bright pixels will not change
    For gamma > 1, the light pixels will be darker and the dark pixel will not change
    """
    
    def __init__(self, gamma: float, mask: Mask = None, mask_threshold: float = 0.99) -> None:
        super().__init__()
        self.gamma = gamma
        self.mask = mask
        self.mask_threshold = mask_threshold  

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int, antialias: bool):
        for surf in surfaces:
            rgb_array = sa.pixels3d(surf)
            if self.mask is None:
                rgb_array[:] = np.clip(((rgb_array/255)**self.gamma * 255).astype(int), 0, 255)
            else:
                if not self.mask.is_loaded():
                    self.mask.load()
                rgb_array[self.mask.matrix > self.mask_threshold] = np.clip(
                    ((rgb_array/255)**self.gamma * 255).astype(int), 0, 255)[self.mask.matrix > self.mask_threshold]

        return surfaces, durations, introduction, index, width, height
