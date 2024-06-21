"""The logger is used to log in-game actions to replay matches after."""

from .utils import get_file
import time
import os
import json
from datetime import datetime

class Logger():
    """
    A logger is used to store the log of a game.
    It might be use to compute statitics, replay actions, ...
    Logs are stored as "data/logs/'timestamp'.log
    """
    def __init__(self) -> None:
        
        self.timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        dir = get_file('data', 'log', dynamic=True)
        if not os.path.exists(dir):
            os.mkdir(dir)
        self._file = get_file('data', f'log/{self.timestamp}.log', True)

    def write(self, data: dict):
        """Write a new line in the log."""

        data['timestamp'] = time.time()
        with open(self._file, 'a') as f:
            json.dump(data, f)
