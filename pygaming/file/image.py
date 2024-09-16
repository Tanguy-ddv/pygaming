"""Image files represent the file of an image."""
import pygame
from .file import File, get_file

class ImageFile(File):
    """Represent the file of an image stored in the assets/images folder."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file(folder='images', file=path)
        self._image = pygame.image.load(self.full_path).convert_alpha()

    def get(self, size: tuple[int, int] | None = None, rotation: float = 0) -> pygame.Surface:
        """
        Get the Surface of the image.
        
        Params:
        ----
        size: tuple(int, int), the expected size of the return image. If no argument is passed, use the size of the image.
        rotation: float, Rotate the image of this amount, default is 0.
        """
        surface = pygame.transform.rotate(self._image, rotation)
        if size is None:
            return surface
        else:
            return pygame.transform.scale(surface, size)
