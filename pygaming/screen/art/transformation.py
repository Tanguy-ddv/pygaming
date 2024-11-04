"""The transformation module contains the base class Transformation and all the subclasses."""
from abc import ABC, abstractmethod
import pygame.transform as tf
from pygame import Surface

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

    def __init__(self, *transfos) -> None:
        super().__init__()
        self._transformations: tuple[Transformation] = transfos
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        for transfo in self._transformations:
            surfaces, durations, introduction, index = transfo.apply(surfaces, durations, introduction, index)