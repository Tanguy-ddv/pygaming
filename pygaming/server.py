"""The server module contains the class Server."""
from .connexion import Server as Network, EXIT, NEW_PHASE
from .database.database import SERVER
from .base import BaseRunnable

class Server(BaseRunnable):
    """The Server is the instance to be run as a server for online game."""

    def __init__(self, nb_max_player: bool, first_phase: str, debug: bool = False) -> None:
        """
        Create the Server.

        Params:
        debug: bool, if True, the database will not delete itself at the end and the logger will also log debug content.
        nb_max_player: The maximum number of player allowed to connect to the game.
        """
        super().__init__(debug, SERVER, first_phase)
        self.network = Network(self.config, nb_max_player)

    def update(self):
        """Update the server."""
        loop_duration = self.clock.tick(self.config.get("max_frame_rate"))
        self.logger.update(loop_duration)
        self.network.update()
        previous = self.current_phase
        is_game_over = self.update_phases(loop_duration)
        if previous != self.current_phase:
            self.network.send_all(NEW_PHASE, self.current_phase)
        return is_game_over

    def stop(self):
        """Stop the event."""
        self.network.send_all(EXIT, '')
        self.network.stop()
