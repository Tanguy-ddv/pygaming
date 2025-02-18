"""This module contains the hitbox class."""

from pygame import Rect

class Hitbox(Rect):

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(self, x, y, width, height)

    def get_at(self, x, y):
        return self.collidepoint(x,y)