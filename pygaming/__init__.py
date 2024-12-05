"""
Pygaming is a python library used to create videogames in python, based on pygame.
Pygaming provide an exhaustive template to create your own offline and online games
by defining your own game phases and transitions between them. Pygaming also
provides settings, loggers, inputs, files, music and sounds, network, and database management,
as well as multi-language support, screen, widgets and frames.
"""
from .config import Config
from .game import Game
from .base import NO_NEXT, STAY
from .logger import Logger
from .phase import ServerPhase, GamePhase
from .server import Server
from .settings import Settings
from .color import Color

from .screen.frame import Frame
from .screen.element import Element

from .screen import anchors

from .screen import widget

from .file import get_file
from .screen.actor import Actor
from .screen import art


from .screen.window import Window, WindowLike
from .screen import mask

from .inputs import Inputs, Controls, Click, Keyboard, Mouse
from .connexion import Client, Server as Network, HEADER, ID, CONTENT, TIMESTAMP

from .database import Database, TypeWriter, SoundBox
from . import commands

__all__ = ['Config', 'Game', 'NO_NEXT', 'STAY', 'Logger', 'ServerPhase', 'GamePhase',
           'Server', 'Settings', 'Frame', 'Actor', 
           'Element', 'Inputs', 'Controls', 'Click', 'widget', 'get_file', 'Client', 'Keyboard', 'Mouse', 'mask', 'art',
           'Network', 'HEADER', 'ID', 'CONTENT', 'TIMESTAMP', 'Database', 'anchors',
           'commands', 'Window', 'WindowLike', 'TypeWriter', 'SoundBox', 'Color']
