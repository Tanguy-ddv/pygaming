import pygame
from .file import File
from .._utils import get_file

class ImageFile(File):
    """Represent the file of an image."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.full_path = get_file(folder='assets/images', path=path)

    def get(self, size: tuple[int, int] = None, rotation: float = 0) -> pygame.Surface:
        surface = pygame.transform.rotate(pygame.image.load(self.full_path).convert_alpha(), rotation)
        if size is None:
            return surface
        else:
            return pygame.transform.scale(surface, size)
        