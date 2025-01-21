"""The server launcher is the file to be turned into an executable. It will execute the server.py"""
import os
import sys
import importlib

def launch_server():
    """Launch the server."""

    current_directory = os.getcwd()

    if current_directory not in sys.path:
        sys.path.append(current_directory)

    importlib.import_module('src.server')

if __name__ == '__main__':
    launch_server()
