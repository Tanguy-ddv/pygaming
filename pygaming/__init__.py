"""
Pygaming is a python library used to create videogames in python, based on pygame.
Pygaming provide an exhaustive template to create your own offline and online games
by defining your own game phases and transitions between them. Pygaming also
provides settings, loggers, inputs, files, music and sounds, network, and database management,
as well as multi-language support, screen, widgets and frames.
"""
from .config import Config
from .font import Font
from .game import Game
from .base import NO_NEXT, STAY
from .logger import Logger
from .phase import ServerPhase, GamePhase
from .server import Server
from .settings import Settings
from .transition import ServerTransition, GameTransition

from .screen.screen import Screen
from .screen.frame import Frame
from .screen.element import Element, TOP_LEFT, TOP_RIGHT, CENTER, BOTTOM_LEFT, BOTTOM_RIGHT
from .screen.animated_surface import AnimatedSurface, SurfaceLike, SurfacesLike

from .inputs import Inputs, Controls, Click
from .file import FontFile, DataFile, ImageFile, GIFFile, SoundFile, MusicFile, get_file
from .connexion import Client, Server as Network, HEADER, ID, CONTENT, TIMESTAMP

from .database import Database, Texts, Speeches
from . import commands
from .screen.colored_surface import ColoredSurface

__all__ = ['Config', 'Font', 'Game', 'NO_NEXT', 'STAY', 'Logger', 'ServerPhase', 'GamePhase',
           'Server', 'Settings', 'ServerTransition', 'GameTransition', 'Screen', 'Frame',
           'Element', 'AnimatedSurface', 'SurfaceLike', 'SurfacesLike', 'Inputs', 'Controls', 'Click', 'FontFile',
           'DataFile', 'ImageFile', 'GIFFile', 'SoundFile', 'MusicFile','get_file', 'Client',
           'Network', 'HEADER', 'ID', 'CONTENT', 'TIMESTAMP', 'Database', 'Texts', 'Speeches',
           'commands', 'ColoredSurface', 'TOP_LEFT', 'TOP_RIGHT', 'CENTER', 'BOTTOM_LEFT', 'BOTTOM_RIGHT']
