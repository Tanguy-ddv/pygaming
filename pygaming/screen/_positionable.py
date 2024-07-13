class Positionable():
    """Positionable is an abstract class for everything having a position: widgets, actors, decors, frames."""

    def __init__(self, x: int, y: int, layer: int = 0) -> None:
        self.x = x
        self.y = y
        self.layer = layer
    
    def move(self, new_x, new_y):
        """Move the object."""
        self.x = new_x
        self.y = new_y
    
    def set_layer(self, new_layer):
        self.layer = new_layer
    
    def send_to_the_back(self):
        self.layer -= 1
    
    def send_to_the_front(self):
        self.layer += 1
    
    @property
    def coordinate(self):
        return (self.x, self.y)