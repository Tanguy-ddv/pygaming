"""The geometry manager module contains the grid, row and columns geometry managers."""

from .anchors import TOP_LEFT, Anchor, CENTER
from dataclasses import dataclass
from itertools import product

@dataclass
class _GridObject:

    width: int
    height: int
    rowspan: int
    columnspan: int

class Grid:

    def __init__(self, x: int, y: int, anchor: int = TOP_LEFT):
        self._x = x
        self._y = y
        self._anchor = anchor
        self._left = self._x
        self._top = self._y
        self._dupl_objects: dict[tuple[int, int], _GridObject] = {} # the matrix of content with duplicated objects for row and column spans.
        self._objects: dict[tuple[int, int], _GridObject] = {} # the matrix of content without duplicate objects for row and column spans.
        self._heights: dict[int, int] = {} # the height of each row
        self._widths: dict[int, int] = {} # the width of each column
    
    def _update(self, row, column, rowspan, columnspan):
        for rw in range(row, row + rowspan):
            self._heights[rw] = self._height_at(rw)
        for col in range(column, column + columnspan):
            self._widths[col] = self._width_at(col)
        
        # Find the new top-left of the grid.
        max_col = max(col for (_, col) in self._dupl_objects)
        max_row = max(row for (row, _) in self._dupl_objects)
        grid_width = sum(self._widths.get(col, 0) for col in range(0, max_col))
        grid_height = sum(self._heights.get(row, 0) for row in range(0, max_row))
        
        self._left = self._x - self._anchor[0]*grid_width
        self._top = self._y - self._anchor[1]*grid_height 

    def add(self, row, column, width, height, rowspan=1, columnspan=1):
        self._objects[(row, column)] = _GridObject(width, height, rowspan, columnspan)
        for rw, col in product(range(row, row + rowspan), range(column, column + columnspan)):
            self._dupl_objects[(rw, col)] = self._objects[(row, column)]
        self._update(row, column, rowspan, columnspan)

    def _width_at(self, column):
        return max((obj.width/obj.columnspan for ((_, col), obj) in self._dupl_objects.items() if col == column), default=0)

    def _height_at(self, row):
        return max((obj.height/obj.rowspan for ((rw, _), obj) in self._dupl_objects.items() if rw == row), default=0)

    def get(self, row, column, anchor: Anchor = TOP_LEFT, justify: Anchor = CENTER):

        obj: _GridObject = self._objects.get((row, column), None)
        if obj is None:
            raise ValueError(f"There is nothing at {row}, {column} in this grid.")
        # The coordinate of the top left of the cell.
        cell_x = sum(self._widths.get(col, 0) for col in range(0, column))
        cell_y = sum(self._heights.get(rw, 0) for rw in range(0, row))
        # The size of the cell
        mutlicol_width = sum(self._widths.get(col, 0) for col in range(column, column + obj.columnspan))
        multirow_height = sum(self._heights.get(rw, 0) for rw in range(row, row + obj.rowspan))
        # The coordinate of the object in the cell
        obj_x = cell_x + justify[0]*(mutlicol_width - obj.width)
        obj_y = cell_y + justify[1]*(multirow_height - obj.height)
        # The position of the anchored point relative to the top-left of the grid.
        rel_x = obj_x + anchor[0]*obj.width
        rel_y = obj_y + anchor[1]*obj.height
        # The position on the master.
        return self._left + rel_x, self._top + rel_y

    def remove(self, row, column):
        if (row, column) in self._objects:
            obj = self._objects[(row, column)]
            del self._objects[(row, column)]
        for rw, col in product(range(row, row + obj.rowspan), range(column, column + obj.columnspan)):
            del self._dupl_objects[(rw, col)]
        self._update(row, column, obj.rowspan, obj.columnspan)
class Column(Grid):

    def __init__(self, x: int, y: int, anchor: int):
        super().__init__(x, y, anchor)
    
    def add(self, row, width, height):
        return super().add(row, 0, width, height, 1, 1)

    def get(self, row, anchor, justify):
        return super().get(row, 0, anchor, justify)
    
    def remove(self, row):
        return super().remove(row, 0)

class Row(Grid):

    def __init__(self, x: int, y: int, anchor: int):
        super().__init__(x, y, anchor)
    
    def add(self, column, width, height):
        return super().add(0, column, width, height, 1, 1)

    def get(self, column, anchor, justify):
        return super().get(0, column, anchor, justify)
    
    def remove(self, column):
        return super().remove(0, column)
