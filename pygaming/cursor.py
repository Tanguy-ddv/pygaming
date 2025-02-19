"""The cursor module contains the cursor class, use to implement various cursors."""
from typing import overload
import os
from pygame import Cursor as _Cs
import pygame
from .screen.art import Art
from .file import get_file
from .settings import Settings

_pygame_system_cursors = [
    'SYSTEM_CURSOR_ARROW', 'SYSTEM_CURSOR_IBEAM', 'SYSTEM_CURSOR_WAIT', 'SYSTEM_CURSOR_CROSSHAIR',
    'SYSTEM_CURSOR_WAITARROW', 'SYSTEM_CURSOR_SIZENWSE', 'SYSTEM_CURSOR_SIZENESW', 'SYSTEM_CURSOR_SIZEWE',
    'SYSTEM_CURSOR_SIZENS', 'SYSTEM_CURSOR_SIZEALL', 'SYSTEM_CURSOR_NO', 'SYSTEM_CURSOR_HAND'
]
_pygame_cursors = [
    'arrow', 'diamond', 'broken_x', 'tri_left', 'tri_right'
]

_pygame_bitmap_cursors = {
    'thickarrow_strings' : ((24, 24), (0, 0)),
    'sizer_x_strings' : ((24, 16), (9, 5)),
    'sizer_y_strings' : ((16, 24), (5, 9)),
    'sizer_xy_strings' : ((24, 16), (5, 7)),
    'textmarker_strings' : ((8, 16), (4,6))
}

def _verify_bitmap(bitmap: tuple[str]):
    max_length = max(len(row) for row in bitmap)
    new_length = max_length + (8 - max_length%8)%8
    rows = [row + ' '*(new_length - len(row)) for row in bitmap]
    while len(rows)%8 > 0:
        rows.append(' '*new_length)
    return tuple(rows)

class Cursor:
    """
    Cursor's are the objects used to show the position of the mouse on the screen.
    They can change dynamically like arts.
    They can be created through a name, in this case it will use the already existing cursor with this name.
    They can be created through one or two paths to xbm files in the assets/cursor folder.
    They can be created through an art
    They can be created through a bitmap.
    """

    @overload
    def __init__(self, cursor_name: str):
        ...

    @overload
    def __init__(self, path: str):
        ...

    @overload
    def __init__(self, curs_path: str, mask_path: str):
        ...

    @overload
    def __init__(self, *cursors: 'Cursor'):
        ...

    @overload
    def __init__(self, art: Art, anchor: tuple[float, float]):
        ...

    @overload
    def __init__(self, bitmap: tuple[str], hotspot: tuple = (0,0)):
        ...

    def __init__(self, *values):
        self.is_loaded = True # only set to false is the cursor is an art
        self._durations = (500,)
        self._introduction = 0
        if len(values) == 1:
            if isinstance(values[0], str):
                if values[0] in _pygame_system_cursors:
                    # Create a cursor with the system cursors
                    self._cursors = (_Cs(getattr(pygame, values[0])),)
                elif values[0] in _pygame_cursors:
                    # Create a cursor with on pygame cursor
                    self._cursors = (getattr(pygame.cursors, values[0]),)
                elif values[0] in _pygame_bitmap_cursors:
                    # Create a cursor with a bitmap cursor
                    self._cursors = (_Cs(*_pygame_bitmap_cursors[values[0]], *pygame.cursors.compile(getattr(pygame.cursors, values[0]))),)
                elif os.path.isfile(get_file('cursors', values[0])):
                    # Create a cursor a file
                    self._cursors = (_Cs(*pygame.cursors.load_xbm(values[0])))
                else:
                    raise ValueError(f"{values[0]} isn't a proper argument for a cursor.")

            elif isinstance(values[0], tuple):
                # Create a cursor with a string bitmap
                bitmap = _verify_bitmap(values[0])
                hotspot = (0, 0)
                size = len(bitmap), len(bitmap[0])

                self._cursors = (_Cs(size, hotspot, *pygame.cursors.compile(bitmap)))

        elif len(values) == 2:

            if isinstance(values[0], Art):
                self.is_loaded = False
                self._cursors = tuple()
                self._future_cursors = values

            elif isinstance(values[0], str):
                if os.path.isfile(get_file('cursors', values[0])) and os.path.isfile(get_file('cursors', values[1])):
                    self._cursors = (_Cs(*pygame.cursors.load_xbm(values[0], values[1])))
                else:
                    raise ValueError(f"{values[0], values[1]} aren't proper arguments for a cursor.")

            elif isinstance(values[0], tuple):
                # Create a cursor with a string bitmap
                bitmap = _verify_bitmap(values[0])
                hotspot = values[1]
                size = len(bitmap), len(bitmap[0])

                self._cursors = (_Cs(size, hotspot, *pygame.cursors.compile(bitmap)))

        if all((isinstance(value, Cursor) for value in values)):
            self._cursors = []
            self._durations = []
            for cursor in values:
                self._cursors.extend(cursor._cursors)
                self._durations.extend(cursor._durations)
            self._cursors = tuple(self._cursors)
            self._durations = tuple(self._durations)

        self._time_since_last_change = 0
        self._index = 0

    def get(self, settings: Settings):
        """Return the current image to show as a cursor."""
        if not self.is_loaded:
            art, anchor = self._future_cursors # pylint: disable=unbalanced-tuple-unpacking
            art.load(**settings)
            hotspot = int(anchor[0]*art.width), int(anchor[1]*art.height)
            self._cursors = tuple(_Cs(hotspot, surf) for surf in art.surfaces)
            self._durations = art.durations
            self._introduction = art.introduction
            self.is_loaded = True
        return self._cursors[self._index]

    def update(self, loop_duration) -> bool:
        """Update the cursor's image to display. Return true if the image changed."""
        if len(self._cursors) > 1:
            self._time_since_last_change += loop_duration
            if self._time_since_last_change >= self._durations[self._index]:
                self._time_since_last_change -= self._durations[self._index]
                self._index += 1
                if self._index == len(self._cursors):
                    self._index = self._introduction
                return True
        return False

    def reset(self):
        """Reset the cursor to its initial state."""
        self._index = 0
        self._time_since_last_change = 0
