"""The logger is used to log in-game actions to replay matches after."""

from .file import get_file
import time
import os
import json
from datetime import datetime

class Logger:
    """
    A logger is used to store the log of a game.
    It might be use to compute statitics, replay actions, ...
    Logs are stored as "data/logs/'timestamp'.log
    """
    def __init__(self, debug: bool = False) -> None:
        
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        dir = get_file('data', 'log', permanent=False)
        self.debug = debug
        if not os.path.exists(dir):
            os.mkdir(dir)
        self._file = open(get_file('data', f'logs/{self.timestamp}.log', True), 'w', encoding='utf-8')

    def write(self, data: dict, is_it_debugging: bool = False):
        """Write a new line in the log."""
        if self.debug or not is_it_debugging:
            data['timestamp'] = time.time()
            json.dump(data, self._file)
    
    def new_log(self):
        """Start a new log."""
        self._file.close()
        self.timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        self._file = open(get_file('data', f'logs/{self.timestamp}.log', True), 'w', encoding='utf-8')

    def __del__(self):
        """At the end of the game, close the file."""
        self._file.close()
    

