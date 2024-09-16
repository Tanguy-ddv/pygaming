"""The GifFile represent the file of a gif, then turned into a list of images and a gif speed."""

import pygame
from PIL import Image
from .file import get_file, File

# import a gif holder and use it to create a list of files.
# do the exact same thing as would be a list of images
# from imagefiles.

class GIFFile(File):
    """A GifFile represent a GIF in the assets/images folder."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file('images', path)
        gif = Image.open(self.full_path)
        gif.seek(0)
        self._images: list[pygame.Surface] = [pygame.image.fromstring(gif.convert('RGBA').tobytes())]
        self._frame_durations = []
        while True:
            try:
                gif.seek(gif.tell()+1)
                self._images.append(pygame.image.fromstring(gif.convert('RGBA').tobytes()))
                self._frame_durations.append(gif.info['duration'])
            except EOFError:
                break

    def get(self, size: tuple[int, int] | None = None, rotation: float = 0):
        images_to_return = []
        for im in self._images:
            surface = pygame.transform.rotate(im, rotation)
            if size is None:
                images_to_return.append(surface)
            else:
                images_to_return.append(pygame.transform.scale(im, size))
        return images_to_return, self._frame_durations
