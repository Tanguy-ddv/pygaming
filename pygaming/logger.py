"""The logger is used to log in-game actions to replay matches after."""

import os
import json
from datetime import datetime
from pygame.time import get_ticks
from .file import get_file
from .config import Config

class Logger:
    """
    A logger is used to store the log of a game.
    It might be used to compute statitics, replay actions, ...
    Logs are stored as "data/logs/'timestamp'.log"
    """
    def __init__(self, config: Config, debug: bool = False, ) -> None:

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        self.time_since_last_flush = 0
        self.config = config
        log_dir = get_file('data', 'logs')
        self.debug = debug
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self._file = open(get_file('data', f'logs/{self.timestamp}.log'), 'a', encoding='utf-8') # pylint: disable=consider-using-with
        # We use this to get the log file always open to save performance with openning and closing.

    def write(self, data: dict, is_it_debugging: bool = False):
        """
        Write a new line in the log.
        
        Params:
        ----
        data: dict, the data to save in the log.
        is_it_debugging: bool, specify if the line is for debugging or not.
        """
        if self.debug or not is_it_debugging:
            data['timestamp'] = get_ticks()
            json.dump(data, self._file)
            self._file.write('\n')

    @property
    def current_file(self):
        """Return the name of the current file."""
        return get_file('data', f'logs/{self.timestamp}.log')

    def update(self, loop_duration: int):
        """Update the logger at every iteration to flush regularly."""
        self.time_since_last_flush += loop_duration
        if self.time_since_last_flush > self.config.get("flush_frequency"):
            self._file.flush()
            self.time_since_last_flush = 0

    def new_log(self):
        """Start a new log."""
        self._file.close()
        self.timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        self._file = open(get_file('data', f'logs/{self.timestamp}.log'), 'a', encoding='utf-8')

    def __del__(self):
        """At the end of the game, close the file."""
        self._file.close()
