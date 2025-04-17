"""The master module defines the Master abstract class implementing methods related to being a master."""
from abc import abstractmethod, ABC
from ..game import Game
from pygame import Rect
from ._grid import Grid
from .anchors import AnchorLike, Anchor, TOP_LEFT

class Master(ABC):
    """The class Master is an abstract for the classes that can be the master of an Element."""

    def __init__(self, window: Rect):
        super().__init__()
        self.children = []
        self.window = window
        self.wc_ratio = (1, 1)
        self.grids: list[Grid] = []
        self.game: Game
        self.absolute_rect: Rect

    def add_child(self, child):
        """Add a new element to the child list."""
        self.children.append(child)

    def create_grid(self, x: int, y: int, anchor: AnchorLike = TOP_LEFT):
        """Create a grid to manage the geomtry of the master."""
        grid = Grid(x, y, Anchor(anchor))
        self.grids.append(grid)
        return grid

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
    def notify_change(self):
        pass

    @abstractmethod
    def notify_change_all(self):
        pass

    @abstractmethod
    def is_visible(self):
        pass

    @abstractmethod
    def is_child_on_me(self, child):
        pass

    @property
    def visible_children(self):
        """Return the list of visible children sorted by increasing layer."""
        return sorted(filter(lambda ch: ch.visible and ch.on_master, self.children), key= lambda w: w.layer)

    @property
    def absolute_left(self):
        """Return the absolute left coordinate of the object on the screen."""
        return self.absolute_rect.left
    
    @property
    def absolute_top(self):
        """Return the absolute top coordinate of the object on the screen."""
        return self.absolute_rect.top
