from .connexion import Server as Network
from .base import Base

class Server(Base):
    pass

    def __init__(self, debug: bool, nb_max_player: bool) -> None:
        """
        Create the Server.

        Params:
        debug: bool, if True, the database will not delete itself at the end and the logger will also log debug content.
        nb_max_player: The maximum number of player allowed to connect to the game.
        """
        super().__init__(debug)
        self.network = Network(nb_max_player)
    
    def update(self):
        """Update the server."""
        is_game_over = self.update_phases()
        return is_game_over