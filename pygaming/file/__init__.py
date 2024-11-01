"""The file module store all the file classes."""
from .font import FontFile, default_font
from .data import DataFile
from .image import ImageFile
from .music import MusicFile
from .file import get_file
from .gif import GIFFile
__all__ = ['FontFile', 'default_font', 'MusicFile', 'ImageFile', 'DataFile', 'get_file', 'GIFFile']
