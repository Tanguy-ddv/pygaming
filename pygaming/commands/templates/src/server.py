"""Use this file to create a server."""
from pygaming import Server, ServerPhase, STAY

class ServerLobby(ServerPhase):

    def __init__(self, server: Server) -> None:
        super().__init__("lobby", server)

    def start(self):
        pass

    def update(self, loop_duration: int):
        pass

    def next(self):
        return ''

    def end(self):
        self.network.send_all("match start", {"color1" : "blue", "color2" : "red"})

    def apply_transition(self, next_phase: str):
        return {"color1" : "blue", "color2" : "red"}


class ServerMacth(ServerPhase):

    def __init__(self, server: Server) -> None:
        super().__init__("match", server)

    def start(self, color1: str, color2: str):
        pass

    def update(self, loop_duration: int):
        pass

    def next(self):
        return STAY

    def end(self):
        pass

    def apply_transition(self, next_phase: str):
        pass

if __name__ == '__main__':
    serv = Server(nb_max_player = 6, first_phase='lobby', debug=True)
    ServerLobby(serv)
    ServerMacth(serv)
    serv.run()
