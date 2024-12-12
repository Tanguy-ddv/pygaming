"""
Pygaming is a python library used to big make 2D games.
Built on pygame, it contains several features to help building big games easily.

Pygaming adds the following features: 
A working directory based on a template,
phases, settings, controls, language, sounds,
screens, frames and widgets,
actors and dynamic sprites, masks

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

from .inputs import Controls, Click, Keyboard, Mouse
from .connexion import Client, Server as Network, HEADER, ID, PAYLOAD, TIMESTAMP

from .database import Database, TypeWriter, SoundBox
from . import commands

__all__ = ['Config', 'Game', 'NO_NEXT', 'STAY', 'Logger', 'ServerPhase', 'GamePhase',
           'Server', 'Settings', 'Frame', 'Actor', 
           'Element', 'Controls', 'Click', 'widget', 'get_file', 'Client', 'Keyboard', 'Mouse', 'mask', 'art',
           'Network', 'HEADER', 'ID', 'PAYLOAD', 'TIMESTAMP', 'Database', 'anchors',
           'commands', 'Window', 'WindowLike', 'TypeWriter', 'SoundBox', 'Color']
