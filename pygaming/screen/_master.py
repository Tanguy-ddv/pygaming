"""The master module defines the Master abstract class implementing methods related to being a master."""
from abc import abstractmethod, ABC
from pygame import Rect
from .camera import Camera

class Master(ABC):
    """The class Master is an abstract for the classes that can be the master of an Element."""

    def __init__(self, camera: Camera, window: Rect):
        super().__init__()
        self.children = []
        self.camera = camera
        self.window = window
        self.wc_ratio = (1, 1)
        self.absolute_rect: Rect
    
    def add_child(self, child):
        """Add a new element to the child list."""
        self.children.append(child)

    @abstractmethod
    def notify_change(self):
        pass

    @abstractmethod
    def notify_change_all(self):
        pass

    def is_child_on_me(self, child):
        """Return whether the child is visible on the phase or not."""
        return self.absolute_rect.colliderect(child.relative_rect)

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
