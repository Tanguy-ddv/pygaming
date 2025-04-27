"""
Pygaming is a python library used to big make 2D games.
Built on pygame, it contains several features to help building big games easily.

Pygaming adds the following features: 
A working directory based on a template,
phases, settings, controls, language, sounds,
screens, frames and widgets,
actors and dynamic sprites, masks
"""
from pygame import Rect
from .game import Game
from ._base import LEAVE, STAY
from .phase import ServerPhase, GamePhase
from .server import Server
from .color import Color

from .screen.frame import Frame
from .screen.hover import Tooltip, TextTooltip, Cursor
from .screen.hitbox import Hitbox
from .screen.states import States

from .screen import anchors, widget, art
from .screen.art import mask, transform

from .file import get_file
from .screen.actor import Actor

from .screen.camera import Camera

from .connexion import HEADER, ID, PAYLOAD, TIMESTAMP

from .database import TextFormatter
from . import commands

__all__ = ['Game', 'LEAVE', 'STAY', 'ServerPhase', 'GamePhase', 'Tooltip', 'TextTooltip',
           'Server', 'Frame', 'Actor', 'TextFormatter', 'Cursor',
           'mask', 'transform', 'widget', 'get_file', 'art', 'States',
           'HEADER', 'ID', 'PAYLOAD', 'TIMESTAMP', 'anchors', 'Rect', 'Hitbox',
           'commands', 'Camera', 'Color']
