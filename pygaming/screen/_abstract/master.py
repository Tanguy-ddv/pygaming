"""The master module defines the Master abstract class implementing methods related to being a master."""
from abc import abstractmethod
from itertools import product
from dataclasses import dataclass
from typing import Any
from pygame import Rect
from .visual import Visual
from ...game import Game
from ..anchors import AnchorLike, Anchor, TOP_LEFT, CENTER_CENTER

@dataclass
class _GridObject:
    """Represent an object in a cell."""

    rowspan: int
    columnspan: int
    padx: int
    pady: int
    element: Any # This is an Element, no direct typing to avoid circular imports
    anchor: Anchor
    justify: Anchor

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

        # Update the position of all elements.
        for (rw, col), obj in self._objects.items():
            element = obj.element
            x, y = self.get(rw, col)
            element._x = x
            element._y = y

    def add(
        self,
        row: int,
        column: int,
        element: Any, # This is an Element, no direct typing to avoid circular imports
        rowspan: int = 1,
        columnspan:int = 1,
        padx: int = 0,
        pady: int = 0,
        anchor: Anchor = TOP_LEFT,
        justify: Anchor = CENTER_CENTER
):
        """
        Add a new cell in the grid.
        
        Params:
        ---
        - row, column: int, the index of the new cell in the grid.
        - element: the element inside the cell.
        - rowspan, columnspan: int, the number of rows and columns the cell we spread across.
        - padx, pady
        - anchor: Anchor, the anchor that will be given to the element at creation.
        - justify: Anchor, specify where the object should placed relatively to its cell
        in case the size of the cell doesn't match the size of the element.

        Raises:
        ---
        - ValueError if the cell already exists and the error_if_exist argument is set to True.
        """
        if any(
            (rw, col) in self._dupl_objects
            for rw, col in product(
                range(row, row + rowspan),
                range(column, column + columnspan)
            )
        ):
            raise ValueError(f"{row, column} already exists in this grid")
        self._objects[(row, column)] = _GridObject(rowspan, columnspan, padx, pady, element, anchor, justify)
        for rw, col in product(range(row, row + rowspan), range(column, column + columnspan)):
            self._dupl_objects[(rw, col)] = self._objects[(row, column)]
        self._update(row, column, rowspan, columnspan)

    def _width_at(self, column):
        return max(((obj.element.width + 2*obj.padx)/obj.columnspan for ((_, col), obj) in self._dupl_objects.items() if col == column), default=0)

    def _height_at(self, row):
        return max(((obj.element.height + 2*obj.pady)/obj.rowspan for ((rw, _), obj) in self._dupl_objects.items() if rw == row), default=0)

    def get(self, row, column):
        """
        Get the coordinate of the anchor of an object placed in the grid.
        
        Params:
        ---
        - row, column: int, the index of the grid cell.

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
        obj_x = cell_x + obj.justify[0]*(mutlicol_width - 2*obj.padx - obj.element.width) + obj.padx
        obj_y = cell_y + obj.justify[1]*(multirow_height - 2*obj.pady - obj.element.height) + obj.pady
        # The position of the anchored point relative to the top-left of the grid.
        rel_x = obj_x + obj.anchor[0]*obj.element.width
        rel_y = obj_y + obj.anchor[1]*obj.element.height
        # The position on the master.
        return self._left + rel_x , self._top + rel_y

    def remove(self, elem):
        """
        Remove a cell from the grid.

        Params:
        ---
        - row, column: int, the index of the cell on the grid.
        - error_if_no: bool, specify the behavior in case of removing a non existing cell. If set to True, an error is raised.

        Raises:
        ---
        - ValueError if the cell does not exist.
        """
        for row, column in self._objects:
            if self._objects[(row, column)].element == elem: 
                obj = self._objects[(row, column)]
                break

        del self._objects[(row, column)]
        for rw, col in product(range(row, row + obj.rowspan), range(column, column + obj.columnspan)):
            del self._dupl_objects[(rw, col)]
        self._update(row, col, obj.rowspan, obj.columnspan)


class Master(Visual):
    """The class Master is an abstract for the classes that can be the master of an Element."""

    def __init__(self):
        super().__init__()
        self.children = set()
        self.wc_ratio: tuple[int, int]
        self.grids: list[Grid] = []
        self.game: Game
        self.absolute_rect: Rect

    def add_child(self, child):
        """Add a new element to the child set."""
        self.children.add(child)

    def create_grid(self, x: int, y: int, anchor: AnchorLike = TOP_LEFT):
        """Create a grid to manage the geometry of the master."""
        grid = Grid(x, y, Anchor(anchor))
        self.grids.append(grid)
        return grid
    
    @abstractmethod
    def is_child_on_me(self, child):
        """Return whether the child is on its master."""
        raise NotImplementedError()

    def get_grid(self, idx: int | Grid | None):
        """
        Return the grid associated with the index.
        """
        if isinstance(idx, Grid):
            return idx
        if idx is None:
            idx = 0
        if -1 < idx < len(self.grids):
            return self.grids[idx]
        else:
            return self.create_grid(0, 0, TOP_LEFT)

    @abstractmethod
    def notify_change_all(self):
        pass

    @property
    def visible_children(self):
        """Return the list of visible children sorted by increasing layer."""
        return sorted(filter(lambda ch: ch.is_visible(), self.children), key= lambda w: w.layer)

    @property
    def master_children(self):
        """Return the list of visible master children."""
        return sorted(filter(lambda ch: ch.is_visible() and isinstance(ch, Master), self.children), key= lambda w: w.layer)