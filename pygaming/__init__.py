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
from .config import Config
from .game import Game
from ._base import LEAVE, STAY
from .logger import Logger
from .phase import ServerPhase, GamePhase
from .server import Server
from .settings import Settings
from .color import Color
from .cursor import Cursor

from .screen.frame import Frame
from .screen.element import Element
from .screen.tooltip import Tooltip, TextTooltip
from .screen.hitbox import Hitbox

from .screen import anchors, widget, art
from .screen.art import mask, transform

from .file import get_file
from .screen.actor import Actor

from .screen.camera import Camera
from .screen.geometry_manager import Grid, Column, Row

from .inputs import Controls, Click, Keyboard, Mouse
from .connexion import Client, Server as Network, HEADER, ID, PAYLOAD, TIMESTAMP

from .database import Database, TypeWriter, SoundBox, TextFormatter
from . import commands

__all__ = ['Config', 'Game', 'LEAVE', 'STAY', 'Logger', 'ServerPhase', 'GamePhase', 'Tooltip', 'TextTooltip',
           'Server', 'Settings', 'Frame', 'Actor', 'TextFormatter', 'Cursor', 'mask', 'transform',
           'Element', 'Controls', 'Click', 'widget', 'get_file', 'Client', 'Keyboard', 'Mouse', 'art',
           'Network', 'HEADER', 'ID', 'PAYLOAD', 'TIMESTAMP', 'Database', 'anchors', 'Rect', 'Hitbox',
           'commands', 'Camera', 'TypeWriter', 'SoundBox', 'Color', 'Grid', 'Column', 'Row']
