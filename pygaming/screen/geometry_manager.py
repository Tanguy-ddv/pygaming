"""The geometry manager module contains the grid, row and columns geometry managers."""
from dataclasses import dataclass
from itertools import product
from .anchors import TOP_LEFT, Anchor, CENTER

@dataclass
class _GridObject:
    """Represent an object in a cell."""

    width: int
    height: int
    rowspan: int
    columnspan: int

class Grid:
    """
    A grid-based layout system that allows placing objects in a structured manner with row and column spanning.

    The grid assigns positions to objects based on their row and column indices and allows for flexible anchoring
    and justification. Each object can span multiple rows and columns, and the system dynamically updates 
    the grid's dimensions and alignment.
    """

    def __init__(self, x: int, y: int, anchor: Anchor = TOP_LEFT):
        self._x = x
        self._y = y
        self._anchor = anchor
        self._left = self._x
        self._top = self._y
        # the matrix of content with duplicated objects for row and column spans.
        self._dupl_objects: dict[tuple[int, int], _GridObject] = {}
        # the matrix of content with non-duplicated objects.
        self._objects: dict[tuple[int, int], _GridObject] = {}
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
        grid_width = sum(self._widths.get(col, 0) for col in range(0, max_col + 1))
        grid_height = sum(self._heights.get(row, 0) for row in range(0, max_row + 1))

        self._left = self._x - self._anchor[0]*grid_width
        self._top = self._y - self._anchor[1]*grid_height 

    def add(self, row, column, width, height, rowspan=1, columnspan=1, error_if_exist=True):
        """
        Add a new cell in the grid.
        
        Params:
        ---
        - row, column: int, the index of the new cell in the grid.
        - width, height: int, the size of the cell.
        - rowspan, columnspan: int, the number of rows and columns the cell we spread across.
        - error_if_exist: bool, whether an error should be raised if a cell is created on an already existing cell.

        Raises:
        ---
        - ValueError if the cell already exists and the error_if_exist argument is set to False.
        """
        if error_if_exist and any(
            (rw, col) in self._dupl_objects
            for rw, col in product(
                range(row, row + rowspan),
                range(column, column + columnspan)
            )
        ):
            raise ValueError(f"{row, column} already exists in this grid")
        self._objects[(row, column)] = _GridObject(width, height, rowspan, columnspan)
        for rw, col in product(range(row, row + rowspan), range(column, column + columnspan)):
            self._dupl_objects[(rw, col)] = self._objects[(row, column)]
        self._update(row, column, rowspan, columnspan)

    def _width_at(self, column):
        return max((obj.width/obj.columnspan for ((_, col), obj) in self._dupl_objects.items() if col == column), default=0)

    def _height_at(self, row):
        return max((obj.height/obj.rowspan for ((rw, _), obj) in self._dupl_objects.items() if rw == row), default=0)

    def get(self, row, column, anchor: Anchor = TOP_LEFT, justify: Anchor = CENTER):
        """
        Get the coordinate of the anchor of an object placed in the grid.
        
        Params:
        ---
        - row, column: int, the index of the grid cell.
        - anchor: Anchor, the anchor that will be given to the element at creation.
        - justify: Anchor, specify where the object should placed relatively to its cell
        in case the size of the cell doesn't match the size of the element.

        Raises:
        ---
        - ValueError if the cell have not been defined yet.

        Notes:
        ---
        If a cell has a columnspan or a rowspan > 1, it must be accessed by the top-left index,
        the same that have been used to create the multirow (or multicolumn) cell.
        """
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

    def remove(self, row, column, error_if_no: bool = False):
        """
        Remove a cell from the grid.

        Params:
        ---
        - row, column: int, the index of the cell on the grid.
        - error_if_no: bool, specify the behavior in case of removing a non existing cell. If set to True, an error is raised.

        Raises:
        ---
        - ValueError if the cell does not exist and error_if_no is set to True.
        """
        if (row, column) in self._objects:
            obj = self._objects[(row, column)]
            del self._objects[(row, column)]
        elif error_if_no:
            raise ValueError(f"The specified cell {row}, {column} do not exist.")
        else:
            return
        for rw, col in product(range(row, row + obj.rowspan), range(column, column + obj.columnspan)):
            del self._dupl_objects[(rw, col)]
        self._update(row, column, obj.rowspan, obj.columnspan)
class Column(Grid):
    """
    A column-based layout system that allows placing objects in a structured manner. A column is a grid with only one different column.
    """

    def __init__(self, x: int, y: int, anchor: Anchor):
        super().__init__(x, y, anchor)

    #pylint: disable=arguments-differ
    def add(self, row: int, width: int, height: int, error_if_exist: bool = True):
        """
        Add a new row.
        
        Params:
        ---
        - row, the index of the row.
        - width, height: int, the size of the cell.
        - exist_ok: bool, whether an error should be raised if a cell is created on an already existing cell.

        Raises:
        ---
        - ValueError if the cell already exists and the error_if_exist argument is set to False.
        """
        return super().add(row, 0, width, height, 1, 1, error_if_exist)

    def get(self, row: int, anchor: Anchor = TOP_LEFT, justify: Anchor = CENTER):
        """
        Get the coordinate of the anchor of an object placed in the grid.
        
        Params:
        ---
        - row: int, the index of the row.
        - anchor: Anchor, the anchor that will be given to the element at creation.
        - justify: Anchor, specify where the object should be placed relatively to its cell
        in case the size of the row doesn't match the size of the element.

        Raises:
        ---
        - ValueError if the row have not been defined yet.
        """
        return super().get(row, 0, anchor, justify)

    def remove(self, row: int, error_if_no: bool = False):
        """
        Remove a row.

        Params:
        ---
        - row: int, the index of the row.
        - error_if_no: bool, specify the behavior in case of removing a non existing row. If set to True, an error is raised.

        Raises:
        ---
        - ValueError if the cell does not exist and error_if_no is set to True.
        """
        return super().remove(row, 0, error_if_no)

class Row(Grid):
    """
    A row-based layout system that allows placing objects in a structured manner. A row is a grid with only one different row.
    """

    def __init__(self, x: int, y: int, anchor: Anchor):
        super().__init__(x, y, anchor)

    #pylint: disable=arguments-differ
    def add(self, column: int, width: int, height: int, error_if_exist: bool = True):
        """
        Add a new column.
        
        Params:
        ---
        - column, the index of the column.
        - width, height: int, the size of the cell.
        - exist_ok: bool, whether an error should be raised if a cell is created on an already existing cell.
    
        Raises:
        ---
        - ValueError if the cell already exists and the error_if_exist argument is set to False.
        """
        return super().add(0, column, width, height, 1, 1, error_if_exist)

    def get(self, column: int, anchor: Anchor = TOP_LEFT, justify: Anchor = CENTER):
        """
        Get the coordinate of the anchor of an object placed in the grid.
        
        Params:
        ---
        - column: int, the index of the column.
        - anchor: Anchor, the anchor that will be given to the element at creation.
        - justify: Anchor, specify where the object should be placed relatively to its cell
        in case the size of the row doesn't match the size of the element.

        Raises:
        ---
        - ValueError if the column have not been defined yet.
        """
        return super().get(0, column, anchor, justify)

    def remove(self, column: int, error_if_no: bool = False):
        """
        Remove a column.

        Params:
        ---
        - row: int, the index of the row.
        - error_if_no: bool, specify the behavior in case of removing a non existing row. If set to True, an error is raised.

        Raises:
        ---
        - ValueError if the cell does not exist and error_if_no is set to True.
        """
        return super().remove(0, column, error_if_no)
