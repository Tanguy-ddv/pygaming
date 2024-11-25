"""The binary transformation file contains transformation that include other arts."""
from pygame import Surface, transform as tf
from ._transformation import Transformation

class Concatenate(Transformation):
    """The concatenate transformation concatenante two arts into one bigger animation."""

    def __init__(self, *others) -> None:
        super().__init__()
        self.others = others
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        need_to_unloads = []
        for art in self.others:
            if not art.is_loaded:
                need_to_unloads.append(True)
                art.load()
            else:
                need_to_unloads.append(False)

        surfaces = surfaces + sum((art.surfaces for art in self.others), ())
        durations = durations + sum((art.durations for art in self.others), ())

        for other, need_to_unload in zip(self.others, need_to_unloads):
            if need_to_unload:
                other.unload()

        return surfaces, durations, introduction, index, width, height

def _combine_arts(*durations: tuple[int], introduction: int) -> tuple[list[tuple[int, tuple[int]]], int]:
    """Combine a list of durations to create a new art."""
    indexes = [0 for _ in durations]
    output = []
    tot_time = 0
    mx = max(sum(d) for d in durations)
    matrix_duration = [list(d) for d in durations]

    output_introduction = None
    for i in range(len(matrix_duration)):
        matrix_duration[i][-1] = matrix_duration[i][-1] + (mx - sum(matrix_duration[i]))

    while tot_time < mx:
        
        if indexes[0] == introduction and output_introduction is None:
            output_introduction = len(output)
        
        mn = min(dur[0] for dur in matrix_duration)
        output.append((mn, tuple(indexes)))



        for i in range(len(matrix_duration)):
            matrix_duration[i][0] -= mn
            if matrix_duration[i][0] == 0:
                matrix_duration[i].pop(0)
                indexes[i] += 1
        tot_time += mn

    return output, output_introduction

class Average(Transformation):
    """
    Take the average of the images of the art.
    """

    def __init__(self, *others) -> None:
        super().__init__()
        self.others = others
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        need_to_unloads = []
        for art in self.others:
            if not art.is_loaded:
                need_to_unloads.append(True)
                art.load()
            else:
                need_to_unloads.append(False)
        
        combined_arts, introduction = _combine_arts(durations, *(other.durations for other in self.others), introduction=introduction)
        new_surfaces = []
        new_durations = []
        all_surfaces = [surfaces] + [other.surfaces for other in self.others]
        for duration, (indexes) in combined_arts:
            avg = tf.average_surfaces([surf[index] for surf, index in zip(all_surfaces, indexes)])
            new_surfaces.append(avg)
            new_durations.append(duration)

        for other, need_to_unload in zip(self.others, need_to_unloads):
            if need_to_unload:
                other.unload()

        return new_surfaces, new_durations, introduction, index, width, height
        
class Blit(Transformation):
    """
    Copy an art over another one.
    """

    def __init__(self, other, x: int, y: int) -> None:
        super().__init__()
        self.other = other
        self.pos = (x,y)
    
    def apply(self, surfaces: tuple[Surface], durations: tuple[int], introduction: int, index: int, width: int, height: int) -> tuple[tuple[Surface], tuple[int], int, int]:
        need_to_unload = False
        if not self.other.is_loaded:
            self.other.load()
            need_to_unload = True
        
        combined_arts, introduction = _combine_arts(durations, self.other.durations, introduction=introduction)
        new_surfaces = []
        new_durations = []
        for duration, (idx1, idx2) in combined_arts:
            back = surfaces[idx1].copy()
            back.blit(self.other.surfaces[idx2], self.pos)
            new_surfaces.append(back)
            new_durations.append(duration)
        
        if need_to_unload:
            self.other.unload()

        return new_surfaces, new_durations, introduction, index, width, height
