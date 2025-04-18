from typing import Self
from pygame import Rect
from ..anchors import Anchor, AnchorLike, TOP_LEFT, CENTER_CENTER
from .master import Master
from .child import Child


class Placable(Child):
    """Object that can be placed."""
    
    def __init__(self, master: Master, update_if_invisible: bool, **kwargs):
        # **kwargs so that the call of super().__init__(...) in the element class can pass every of its argument to Placable.
        super().__init__(master=master, update_if_invisible=update_if_invisible, add_to_master=True)
        self._x = None
        self._y = None
        self.anchor = None
        self.layer = None
        self.on_master = False
        self._current_grid = None # None or a Grid.
        # All placable must have an absolute rect. It can either be based on a background, like most Elements but Frames
        # Or it can be defined differently, like Frames, Phases or Views.
        self.absolute_rect: Rect

    def get_on_master(self):
        """Reassign the on_screen argument to whether the object is inside the screen or outside."""
        on_screen = self.absolute_rect.colliderect((0, 0, *self.master.game.config.dimension))
        self.on_master = on_screen and self.master.is_child_on_me(self)

    def place(self, x: int, y: int, anchor: AnchorLike = TOP_LEFT, layer=0):
        """
        Place the element on its master.
        
        :param x: int, the horizontal coordinate in the master, of the anchor.
        :param y: int, the vertical coordinate in the master, of the anchor.
        :param anchor: Anchor, the anchor point of the element that will be placed at the coordinate (x,y)
        :param layer: int, the z-coordinate of the element, used to manage the order of display and interaction.

        :return self: Element, the element itself is returned allowing method chaining.
        """

        # Remove the element from the grid.
        if self._current_grid is not None:
            self._current_grid.remove(self)
            self._current_grid = None

        self._x = x
        self._y = y
        self.anchor = Anchor(anchor)
        self.layer = layer

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()
        
        return self

    def grid(self,
        row: int,
        column: int,
        grid = None,
        rowspan: int = 1,
        columnspan: int = 1,
        padx: int = 0,
        pady: int = 0,
        anchor: AnchorLike = TOP_LEFT,
        justify: AnchorLike = CENTER_CENTER,
        layer: int = 0
    ) -> Self:
        """
        Place the element on its master using a grid.
        
        :param row: int, The row on the grid this element is placed on.
        :param column: int, The column on the grid this element is placed on.
        :param grid: int = None, Grid or None. If None, then the first grid is used. If an int is provided, the grid-th grid of the master is used.
            If the master do not have a grid-th Grid, then it is created with an anchor of TOP_LEFT and coordinates of 0, 0.
            If a Grid is provided (an object created by master.create_grid(...)), then it is used.
        :param rowspan: int = 1 the number of row the element can span across
        :param: columnspan: int = 1 the number of columns the element can span across
        :param padx: int = 0 the number of pixels added on the left and right of the element
        :param pady: int = 0 the number of pixels added above and below the element
        :param anchor: Anchor = TOP_LEFT, the anchor of the element.
        :param justify: Anchor = CENTER. In case the cell is larger than the element, this is used to specify where the element should be aligned
        :param layer: int, the z-coordinate of the element, used to manage the order of display and interaction.

        :return self: Element, the element itself is returned allowing method chaining.
        """

        if self._current_grid is not None:
            self._current_grid.remove(self)

        grid = self.master.get_grid(grid)
        self.anchor = Anchor(anchor)
        grid.add(row, column, self, rowspan, columnspan, padx, pady, self.anchor , Anchor(justify))
        self._current_grid = grid
        self._x, self._y = grid.get(row, column)
        self.layer = layer

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()

        return self

    def move(self, dx: int = 0, dy: int = 0):
        """
        Move the element on its master. if the element is not placed yet, nothing happen.
        
        Params:
        ---
        - dx: int = 0, the number of pixel by which the element should be translated horizontally
        - dy: int = 0, the number of pixel by which the element should be translated vertically

        Note:
        ----
        If the element has been placed with grid, it is removed from the grid.
        """

        if self._x is None:
            return

        # Remove the element from the grid.
        if self._current_grid is not None:
            self._current_grid.remove(self)
            self._current_grid = None

        self._x += dx
        self._y += dy

        self.get_on_master()
        if self.on_master:
            self.master.notify_change()

    @property
    def relative_rect(self):
        return Rect(self._x, self._y, self.width, self.height)

    @property
    def relative_coordinate(self):
        """Reutnr the relative coordinate of the element in its frame."""
        return (self.relative_left, self.relative_top)

    @property
    def absolute_coordinate(self):
        """Return the coordinate of the element in the game window."""
        return (self.absolute_left, self.absolute_top)

    @property
    def relative_rect(self):
        """Return the rect of the element in its frame."""
        return Rect(self.relative_left, self.relative_top, self.width, self.height)

    @property
    def absolute_rect(self):
        """Return the rect of the element in the game window."""
        return Rect(self.absolute_left, self.absolute_top, self.width*self.master.wc_ratio[0], self.height*self.master.wc_ratio[1])

    @property
    def shape(self):
        """Return the shape of the element"""
        return (self.width, self.height)

    @property
    def relative_right(self):
        """Return the right coordinate of the element in the frame."""
        return self.relative_left + self.width

    @property
    def absolute_right(self):
        """Return the right coordinate of the element in the game window"""
        return self.absolute_left + self.width*self.master.wc_ratio[0]

    @property
    def relative_bottom(self):
        """Return the bottom coordinate of the element in the frame."""
        return self.relative_top + self.height

    @property
    def absolute_bottom(self):
        """Return the bottom coordinate of the element in the game window."""
        return self.absolute_top + self.height*self.master.wc_ratio[1]

    @property
    def relative_left(self):
        """Return the left coordinate of the element in the frame."""
        return self._x - self.anchor[0]*self.width

    @property
    def absolute_left(self):
        """Return the left coordinate of the element in the game window."""
        return self.master.absolute_rect.left + self.relative_left*self.master.wc_ratio[0]

    @property
    def relative_top(self):
        """Return the top coordinate of the element in the frame."""
        return self._y - self.anchor[1]*self.height

    @property
    def absolute_top(self):
        """Return the top coordinate of the element in the game window."""
        return self.master.absolute_rect.top + self.relative_top*self.master.wc_ratio[1]
