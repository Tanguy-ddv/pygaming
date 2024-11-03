"""The file module store all the file classes."""
from .data import DataFile
from .image import ImageFile
from .file import get_file
from .gif import GIFFile
__all__ = ['default_font', 'ImageFile', 'DataFile', 'get_file', 'GIFFile']
