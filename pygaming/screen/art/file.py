"""The file module contains classes to open images, gifs and folders as arts."""
from typing import Iterable
from PIL import Image
from pygame.image import load, fromstring
from .art import Art
from .transformation import Transformation
from ...file import get_file
import os
from ...error import PygamingException

class ImageFile(Art):
    """
    The ImageFile class is an Art loaded from an image in the assets/images folder.
    Accepted format are: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm
    
    Example:
    ---
    ImageFile("my_image.png") is an Art displaying the image stored at "assets/images/my_image.png"
    ImageFile("characters/char1.jpeg") is an Art displaying the image stored at "assets/images/characters/char1.jpeg"
    """

    def __init__(self, file: str, transformation: Transformation = None, force_load_on_start: bool = False) -> None:
        super().__init__(transformation, force_load_on_start)
        self.full_path = get_file('images', file)
        self._width, self._height = Image.open(self.full_path).size
        self._find_initial_dimension()
    
    def _load(self):
        self.surfaces = (load(self.full_path),)
        self.durations = (0,)

class ImageFolder(Art):
    """
    The ImageFolder class is an Art loaded from multiple images in a folder of assets/images folder.
    All image must have one of these formats: jpg, jpeg, png, gif (only first frame), svg, webp, lmb, pcx, pnm, tga (uncompressed), xpm
    The animation is reconstructed by taking images in the alphabetical order from the file. All images must have the same sizes
    
    Example:
    -----
    - ImageFolder("my_images/", [100, 200, 100]) is an Art displaying the images stored in the folder "assets/images/my_images/". The folder contains 3 images
    and the animation will be 400 ms, 100 ms for the first image, 200 ms for the second, and 100 for the last
    - ImageFolder("characters/char1/running/, 70) is an Art displaying the images stored in the folder "assets/images/characters/char1/running/".
    Every images in the folder will be display 70 ms.
    - ImageFolder("my_images/", 70, 10) is an Art displaying the images stored in the folder "assets/images/my_images/". The folder contains at least 10 images.
    When all the images have been displayed, do not loop on the very first but on the 10th.
    """

    def __init__(self, folder: str, durations: Iterable[int] | int, introduction: int = 0, transformation: Transformation = None, force_load_on_start: bool = False) -> None:
        super().__init__(transformation, force_load_on_start)
        self.full_path = get_file('images', folder)
        self.durs = durations
        self._introduction = introduction
        
        self._paths = [os.path.join(self.full_path, f) for f in os.listdir(self.full_path) if os.path.isfile(os.path.join(self.full_path, f))]
        self._width, self._height = Image.open(self._paths[0]).size
        self._find_initial_dimension()
    
    def _load(self):
        self.surfaces = (load(path) for path in self._paths)
        if self._introduction > len(self.surfaces):
            raise PygamingException(f"The introduction specified for this ImageFolder is too high, got {self._introduction} while there is only {len(self.surfaces)} images.")
        if isinstance(self.durs, int):
            self.durations = (self.durs for _ in self.surfaces)
        else:
            if len(self.durs) != len(self.surfaces):
                raise PygamingException(
                    f"The length of the durations list ({len(self.durs)}) does not match the len of the number of images ({len(self.surfaces)})"
                )
            self.durations = tuple(self.durs)
        self._verify_sizes()

class GIFFile(Art):
    """
    The GIFFile is an Art that display a gif stored in the assets/images file
    
    Example:
    -----
    - GIFFile("my_animation.gif") is an Art displaying the gif stored at "assets/images/my_animation.gif".
    - GIFFile("my_animation.gif", 10) is an Art displaying the gif stored at "assets/images/my_animation.gif". The gif mut have at least 10 images.
    When all the images have been displayed, do not loop on the very first but on the 10th.
    """

    def __init__(self, file: str, transformation: Transformation = None, introduction: int = 0, force_load_on_start: bool = False) -> None:
        super().__init__(transformation, force_load_on_start)
        self.full_path = get_file('images', file)
        self._introduction = introduction
        self._width, self._height = Image.open(self.full_path).size
        self._find_initial_dimension()

    def _load(self):
        gif = Image.open(self.full_path)
        gif.seek(0)
        images = [fromstring(gif.convert('RGBA').tobytes(), gif.size, 'RGBA')]
        image_durations = [gif.info['duration']]
        while True:
            try:
                gif.seek(gif.tell()+1)
                images.append(fromstring(gif.convert('RGBA').tobytes(), gif.size, 'RGBA'))
                image_durations.append(gif.info['duration'])
            except EOFError:
                break
        self.surfaces = tuple(images)
        self.durations = tuple(image_durations)

        if self._introduction > len(self.surfaces):
            raise PygamingException(f"The introduction specified for this ImageFolder is too high, got {self._introduction} while there is only {len(self.surfaces)} images.")
        