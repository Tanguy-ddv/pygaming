from gamarts import *
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

class ImageFile(ImageFile):

    def __init__(self, path, transparency = True, transformation = None):
        file = get_file('images', path)
        super().__init__(file, transparency, transformation)

class ImageFolder(ImageFolder):

    def __init__(self, path, durations, introduction = 0, transformation = None):
        folder = get_file('images', path)
        super().__init__(folder, durations, introduction, transformation)

class GIFFile(GIFFile):

    def __init__(self, path, introduction = 0, transformation = None):
        file = get_file('image', path)
        super().__init__(file, introduction, transformation)
