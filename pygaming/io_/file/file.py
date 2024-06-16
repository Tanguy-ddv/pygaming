import sys
import os
import pygame
from abc import ABC, abstractmethod
from typing import Literal


class File(ABC):

    def __init__(self, path: str) -> None:
        self.path = path
        self.fullpath = None