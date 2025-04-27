"""the canvas module defined the canvas widget used to draw."""

from pygame.surface import Surface as Surface
from .._abstract import GraphicalChild, Placeable
from ..frame import Frame
from ..art.art import Art
from ..art import transform
from ...file import get_file

class Canvas(GraphicalChild, Placeable):
    """A Widged used to draw objects on."""

    def __init__(
        self,
        master: Frame,
        background: Art,
    ) -> None:
        super().__init__(
            master=master,
            art=background,
            update_if_invisible=False
        )
        self._transfos = []
        self._index = 0
        self._background_copy = background.copy()
    
    def begin(self):
        self._background_copy.start(**self.game.settings)
        super().begin()

    def previous(self):
        if self._index > 0:
            self._index -= 1
            if self._index > 0:
                pipeline = transform.Pipeline(*self._transfos[:self._index])
            else:
                pipeline = None
            self._background_copy = self._arts.main.copy(pipeline)
            self.notify_change()
            return True
        return False

    def next(self):
        if self._index < len(self._transfos):
            self._index += 1
            self._background_copy.transform(self._transfos[self._index-1])
            self.notify_change()
            return True
        return False

    def transform(self, transfo: transform.Transformation):
        self._transfos = self._transfos[:self._index] # discard the undone transformations
        self._transfos.append(transfo)
        self._index += 1
        self._background_copy.transform(transfo)
        self.notify_change()
    
    def draw_line(self, color, p1, p2, thickness: int = 0, allow_antialias: bool = True):
        transfo = transform.DrawLine(color, p1, p2, thickness, allow_antialias)
        self.transform(transfo)

    def draw_lines(self, color, points, thickness: int = 0, closed: bool=False, allow_antialias: bool = True):
        transfo = transform.DrawLines(color, points, thickness, closed, allow_antialias)
        self.transform(transfo)

    def draw_polygon(self, color, points, thickness: int = 0, allow_antialias: bool = True):
        transfo = transform.DrawPolygon(color, points, thickness, allow_antialias)
        self.transform(transfo)

    def draw_circle(self, color, radius, center, thickness: int = 0, allow_antialias: bool = True):
        transfo = transform.DrawCircle(color, radius, center, thickness, allow_antialias)
        self.transform(transfo)

    def draw_ellipse(self, color, radius_x, radius_y, center, thickness: int = 0, angle:int = 0, allow_antialias: bool = True):
        transfo = transform.DrawEllipse(color, radius_x, radius_y, center, thickness, angle, allow_antialias)
        self.transform(transfo)

    def draw_rectangle(self, color, rect, thickness: int = 0, allow_antialias: bool = True):
        transfo = transform.DrawRectangle(color, rect, thickness, allow_antialias)
        self.transform(transfo)
    
    def draw_rounded_rectangle(self,color, rect, top_left, top_right = None, bottom_right = None, bottom_left = None, thickness: int = 0, allow_antialias: bool = True):
        transfo = transform.DrawRoundedRectangle(color, rect, top_left, top_right, bottom_right, bottom_left, thickness, allow_antialias)
        self.transform(transfo)

    def make_surface(self) -> Surface:
        return self._background_copy.get(self._arts.main, **self.game.settings)

    def save(self, path):
        self._background_copy.save(get_file('image'), path)
