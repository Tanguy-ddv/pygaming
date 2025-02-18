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
    __art_save(self, get_file('image', path), index)

Art.save = __new_save

class ImageFile(ImageFile):

    def __init__(self, path, transparency = True, transformation = None):
        file = get_file('image', path)
        super().__init__(file, transparency, transformation)

class ImageFolder(ImageFolder):

    def __init__(self, path, durations, introduction = 0, transformation = None):
        folder = get_file('image', path)
        super().__init__(folder, durations, introduction, transformation)

class GIFFile(GIFFile):

    def __init__(self, path, introduction = 0, transformation = None):
        file = get_file('image', path)
        super().__init__(file, introduction, transformation)
