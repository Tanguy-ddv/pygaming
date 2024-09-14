"""Use this file to create a server."""
from typing import Any
from pygaming import Server, ServerPhase, ServerTransition

class ServerLobby(ServerPhase):
    
    def __init__(self, server: Server) -> None:
        super().__init__("lobby", Server)
    
    def start(self):
        pass

    def _update(self, loop_duration: int):
        pass

    def next(self):
        return ''
    
    def end(self):
        self.network.send_all("match start", {"color1" : "blue", "color2" : "red"})

class ServerMacth(ServerPhase):

    def __init__(self, server: Server) -> None:
        super().__init__("match", Server)

    def start(self, color1: str, color2: str):
        pass

    def _update(self, loop_duration: int):
        pass

    def next(self):
        return ''
    
    def end(self):
        pass

class ServerLobbyMatchTransition(ServerTransition):

    def __init__(self, server: Server) -> None:
        super().__init__(Server, "lobby", "match")

    def apply(self, phase: ServerLobby) -> dict[str, Any]:
        return {"color1" : "blue", "color2" : "red"}

if __name__ == '__main__':
    server = Server(debug = False, nb_max_player = 6)
    ServerLobby(server)
    ServerMacth(server)
    ServerLobbyMatchTransition(server)
    server.run()