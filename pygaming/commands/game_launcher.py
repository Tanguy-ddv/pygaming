"""The game launcher is the file to be turned into an executable. It will execute the game.py"""
import os
import sys
import importlib

def launch_game():
    """Launch the game."""

    current_directory = os.getcwd()

    if current_directory not in sys.path:
        sys.path.append(current_directory)

    importlib.import_module('src.game')

if __name__ == '__main__':
    launch_game()
