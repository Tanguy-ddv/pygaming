"""The transformation module contains the base class Transformation and all the subclasses."""
from abc import ABC, abstractmethod
import pygame.transform as tf
from pygame import Surface
from pygame import Rect

class Transformation(ABC):

    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def apply(
        self,
        surfaces: tuple[Surface],
        durations: tuple[int],
        introduction: int,
        index: int
    ) -> tuple[tuple[Surface], tuple[int], int, int]:
        """Apply the transformation"""
        raise NotImplementedError()
    
class TransformationPipeline(Transformation):
    """A Transformation pipeline is a successive list of transformations."""

    def __init__(self, *transfos) -> None:
        super().__init__()
        self._transformations: tuple[Transformation] = transfos
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        for transfo in self._transformations:
            surfaces, durations, introduction, index = transfo.apply(surfaces, durations, introduction, index)

class Rotate(Transformation):
    
    def __init__(self, angle: float) -> None:
        super().__init__()
        self.angle = angle

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        rotated_surfaces = (tf.rotate(surf, self.angle) for surf in surfaces)
        return rotated_surfaces, durations, introduction, index

class Rescale(Transformation):

    def __init__(self, scale: float) -> None:
        super().__init__()
        self.scale = scale
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        w, h = surfaces[0].get_size()
        new_w, new_h = int(w*self.scale), int(h*self.scale)
        rescaled_surfaces = (tf.scale(surf, (new_w, new_h)) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index

class Resize(Transformation):

    def __init__(self, size: tuple[int, int]) -> None:
        super().__init__()
        self.size = size
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        rescaled_surfaces = (tf.scale(surf, self.size) for surf in surfaces)
        return rescaled_surfaces, durations, introduction, index

class Subsurface(Transformation):

    def __init__(self, rect: Rect) -> None:
        super().__init__()
        self.rect = rect

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        subsurfaces = (surf.subsurface(self.rect) for surf in surfaces)
        return subsurfaces, durations, introduction, index

class SetAlpha(Transformation):

    def __init__(self, alpha: int) -> None:
        super().__init__()
        self.alpha = alpha

    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        alpha_surfaces = (surf.set_alpha(self.alpha) for surf in surfaces)
        return super().apply(alpha_surfaces, durations, introduction, index)