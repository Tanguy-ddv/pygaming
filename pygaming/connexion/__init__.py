"""The connexion module contains the client and server classes as well as some useful constants."""
from .client import Client
from .server import Server
from ._constants import ID, HEADER, PAYLOAD, EXIT, NEW_PHASE, DISCONNECTION, TIMESTAMP
__all__ = ['Client', 'Server', 'ID', 'HEADER', 'PAYLOAD', 'EXIT', 'NEW_PHASE', 'DISCONNECTION', 'TIMESTAMP']
