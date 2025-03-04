from gamarts import (
    GIFFile as _GIFFile, ImageFile as _ImageFile, ImageFolder as _ImageFolder, Rectangle, RoundedRectangle, Circle, Ellipse, Polygon,
    TexturedCircle, TexturedEllipse, TexturedPolygon, TexturedRoundedRectangle, Art
)
# reexport of all arts, some are slightly modified to use the get_file function
from ...file import get_file

# Update the saving method of the art by using the get_file function.
__art_save = Art.save
def __new_save(self, path: str, index: int | slice = None):
    """
    Save the art.
    
    Params:
    ---
    - path: str, the path in the assets/images folder to save the art
    - index: int or slice. If an int is provided or if there is only one frame in the art, only one frame is saved.
    if a slice is provided, the frames in the slice are saved as a gif
    if nothing is provided, all frames are saved as gif (or as an image, if there is only one.)
    """
    __art_save(self, get_file('images', path), index)
Art.save = __new_save

# Update the init to add the permanent and load_on_start arguments.
__art_init = Art.__init__
def __new_init(self, transformation):
    __art_init(self, transformation)
    self._permanent = False
    self._load_on_start = False
Art.__init__ =  __new_init

# Add a copy at get time.
__art_get = Art.get
Art.get = lambda self, match, copy = True, **kwargs: __art_get(self, match, **kwargs).copy() if copy else __art_get(self, match, **kwargs)

# Add load on start and permanent, with start and end.
def __set_load_on_start(self):
    self._load_on_start = True
    return self

def __set_permanent(self):
    self._permanent = True
    return self

Art.set_load_on_start = __set_load_on_start
Art.set_permanent = __set_permanent

def __start(self, **ld_kwargs):
    if self._load_on_start:
        self.load(**ld_kwargs)

def __end(self):
    if not self._permanent:
        self.unload()

Art.start = __start
Art.end = __end

class ImageFile(_ImageFile):
    """
    The ImageFile class is an Art loaded from an image.
    Accepted format are: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm

    Example:
    ---
    - ``ImageFile("my_image.png")`` is an Art displaying the image stored at "my_image.png"
    - ``ImageFile("characters/char1.jpeg", False)`` will load an the image stored at "characyers/char1.jpeg" and convert it in the RGB format
    """

    def __init__(self, path, transparency = True, transformation = None):
        file = get_file('images', path)
        super().__init__(file, transparency, transformation)

class ImageFolder(_ImageFolder):
    """
    The ImageFolder class is an Art loaded from multiple images in a folder.
    All image must have one of these formats: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm
    The animation is reconstructed by taking images in the alphabetical order from the file. All images must have the same sizes
    
    Example:
    -----
    - ``ImageFolder("my_images/", [100, 200, 100])``
    is an Art displaying the images stored in the folder "assets/images/my_images/".
    The folder contains 3 images and the animation will be 400 ms, 100 ms for the first image, 200 ms for the second, and 100 for the last
    - ``ImageFolder("characters/char1/running/", 70)`` is an Art displaying the images stored in the folder "assets/images/characters/char1/running/".
    Every images in the folder will be display 70 ms.
    - ``ImageFolder("my_images/", 70, 5)`` is an Art displaying the images stored in the folder "assets/images/my_images/".
    The folder must contains at least 5 images.
    When all the images have been displayed, it does not loop on the very first but on the 6th.
    Frame will be displayed in the following order, if there are 9 frames:
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 5, 6, 7, 8, 5, 6, 7, 8, 5, 6, ...].
    """

    def __init__(self, path, durations, introduction = 0, transformation = None):
        folder = get_file('images', path)
        super().__init__(folder, durations, introduction, transformation)

class GIFFile(_GIFFile):
    """
    The GIFFile is an Art that displays a gif.
    
    Example:
    -----
    - GIFFile("my_animation.gif") is an Art displaying the gif stored at "assets/images/my_animation.gif".
    - GIFFile("my_animation.gif", 10) is an Art displaying the gif stored at "assets/images/my_animation.gif".
    it must have at least 10 images.
    When all the images have been displayed, do not loop on the very first but on the 10th.
    """

    def __init__(self, path, introduction = 0, transformation = None):
        file = get_file('image', path)
        super().__init__(file, introduction, transformation)

__all__ = [
    'GIFFile', 'ImageFile', 'ImageFolder', 'Rectangle', 'RoundedRectangle', 'Art',
    'Circle', 'Ellipse', 'Polygon', 'TexturedCircle', 'TexturedEllipse', 'TexturedPolygon',
    'TexturedRoundedRectangle'
]