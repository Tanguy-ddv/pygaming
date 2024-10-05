"""Use this file to create a game."""
from pygaming import Game, GamePhase
from pygaming import HEADER

class GameLobby(GamePhase):

    def __init__(self, game: Game) -> None:
        super().__init__("lobby", game)
        self.is_ready = False
        self.chosen_color = "blue"

    def start(self):
        pass

    def update(self, loop_duration: int):

        self.network.send("my choice", {"color" : self.chosen_color, "ready": self.is_ready})
        # Use inputs to choose a new color
        # Use screen to display choices
        # Use soundbox and Jukebox for the sounds and music
        # ....

    def next(self):
        return "match" if any(lr[HEADER] == "match start" for lr in self.network.last_receptions) else ''

    def end(self):
        pass

    def apply_transition(self, next_phase: str):
        return {"color1" : self.chosen_color, "color2" : "red"}

class GameMacth(GamePhase):

    def __init__(self, game: Game) -> None:
        super().__init__("match", game)

    def start(self, color1: str, color2: str):
        pass

    def update(self, loop_duration: int):
        pass

    def next(self):
        return ''

    def end(self):
        pass

    def apply_transition(self, next_phase: str):
        pass

if __name__ == '__main__':
    gm = Game(first_phase="lobby", debug = False)
    GameLobby(gm)
    GameMacth(gm)
    gm.run()
