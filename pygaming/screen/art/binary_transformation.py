"""The binary transformation file contains transformation that include other arts."""
from typing import Iterable
from pygame import Surface
from .transformation import Transformation
from .art import Art

class Concatenate(Transformation):

    def __init__(self, other: Art) -> None:
        super().__init__()
        self.other = other
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        need_to_unload = False
        if not self.other.is_loaded:
            self.other.load()
            need_to_unload = True

        surfaces = (*surfaces, *self.other.surfaces)
        durations = (*durations, *self.other.durations)
        if need_to_unload:
            self.other.unload()

        return surfaces, durations, introduction, index
