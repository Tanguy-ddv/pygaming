"""The art module contains the arts, masks and transformations. Arts are used to represent any image, animated or not, on the screen."""
from typing import Callable
from gamarts import mask
from gamarts import transform
from .art import *

# Update the FromImageColor mask.
__fic_init = mask.FromImageColor.__init__
def __new_fic_init(self, path: str, function: Callable[[int, int, int], float]):
    """
    Create a mask from an image.
    
    Params:
    ---
    - path: str, the path of the image inside the assets/images folder.
    - function: r,g,b -> float, a function mapping a color into a value for the mask.
    """
    __fic_init(self, get_file('image', path), function)
mask.FromImageColor.__init__ = __new_fic_init

mask.Mask.get_at = lambda self, pos: self.matrix.shape[0] >= pos[0] >= 0 and self.matrix.shape[1] >= pos[1] >= 0 and bool(self.matrix[*pos])

del Callable
