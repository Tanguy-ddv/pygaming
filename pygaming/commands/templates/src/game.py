"""Use this file to create a game."""
from typing import Any
from pygaming import Game, GamePhase, GameTransition
from pygaming import HEADER, CONTENT

class GameLobby(GamePhase):
    
    def __init__(self, game: Game) -> None:
        super().__init__("lobby", game)
        self.is_ready = False
        self.chosen_color = "blue"
    
    def start(self):
        pass

    def _update(self, loop_duration: int):
        
        self.network.send("my choice", {"color" : self.chosen_color, "ready": self.is_ready})
        # Use inputs to choose a new color
        # Use screen to display choices
        # Use soundbox and Jukebox for the sounds and music
        # ....

    def next(self):
        return "match" if any(lr[HEADER] == "match start" for lr in self.network.last_receptions) else ''
    
    def end(self):
        pass

class GameMacth(GamePhase):

    def __init__(self, game: Game) -> None:
        super().__init__("match", game)

    def start(self, color1: str, color2: str):
        pass

    def _update(self, loop_duration: int):
        pass

    def next(self):
        return ''
    
    def end(self):
        pass

class GameLobbyMatchTransition(GameTransition):

    def __init__(self, game: Game) -> None:
        super().__init__(game, "lobby", "match")

    def apply(self, phase: GameLobby) -> dict[str, Any]:
        return {"color1" : phase.chosen_color, "color2" : "red"}

if __name__ == '__main__':
    game = Game(online = True, debug = False)
    GameLobby(game)
    GameMacth(game)
    GameLobbyMatchTransition(game)
    game.run()