"""The GifFile represent the file of a gif, then turned into a list of images and a gif speed."""

import pygame
from PIL import Image
from .file import get_file, File

class GIFFile(File):
    """A GifFile represent a GIF in the assets/images folder."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file('images', path)

    def get(self, size: tuple[int, int] | None = None, rotation: float = 0):
        """Get the gif as a list of surfaces and frame durations."""
        gif = Image.open(self.full_path)
        gif.seek(0)
        images: list[pygame.Surface] = [pygame.image.fromstring(gif.convert('RGBA').tobytes(), gif.size, 'RGBA')]
        frame_durations = [gif.info['duration']]
        while True:
            try:
                gif.seek(gif.tell()+1)
                images.append(pygame.image.fromstring(gif.convert('RGBA').tobytes(), gif.size, 'RGBA'))
                frame_durations.append(gif.info['duration'])
            except EOFError:
                break

        images_to_return = []
        for im in images:
            surface = pygame.transform.rotate(im, rotation)
            if size is None:
                images_to_return.append(surface)
            else:
                images_to_return.append(pygame.transform.scale(im, size))
        return images_to_return, frame_durations
