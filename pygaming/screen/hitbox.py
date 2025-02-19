"""This module contains the hitbox class."""

from pygame import Rect

class Hitbox(Rect):

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)

    def get_at(self, pos: tuple[int, int]):
        return self.collidepoint(pos)