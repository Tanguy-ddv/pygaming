import pygaming as pgg
import numpy.random as rd
import math
from numpy import sign

class Player:

    def __init__(self, id_: int, color: pgg.Color, name: str):
        self.id = id_
        self.color = color
        self.name = name
        self.x, self.y = rd.randint(10, 800 - 50), rd.randint(20, 580)
        self.is_connected = True
        self.angle = rd.randint(0, 360)/180*math.pi
        self.score = 0
    
    def rejoin(self, new_color: pgg.Color, new_name: str):
        self.color = new_color
        self.name = new_name
        self.is_connected = True
    
    def leave(self):
        self.is_connected = False

    def turn(self, loop_duration, left: bool, right: bool):
        if left:
            self.angle += loop_duration/180*math.pi/2
        if right:
            self.angle -= loop_duration/180*math.pi/2
    
    def update(self, loop_duration):

        self.x += math.cos(self.angle)*loop_duration/6
        self.y += math.sin(self.angle)*loop_duration/6

        self.score += loop_duration

        if (self.y < 0 or self.y > 560) and sign(math.sin(self.angle)) == sign(self.y):
            self.angle = -self.angle % (2*math.pi)
        if (self.x < 20 or self.x > 780) and sign(math.cos(self.angle)) == sign(self.x - 20):
            self.angle = (math.pi - self.angle) % (2*math.pi)

class ServerPhase(pgg.ServerPhase):

    def __init__(self, server):
        super().__init__('game', server)
        self.players: list[Player] = []

    def next(self):
        return pgg.STAY

    def apply_transition(self, next_phase):
        return {}

    def update(self, loop_duration):
        current_state = {
            player.name : {
                'red' : player.color.r,
                'green' : player.color.g,
                'blue' : player.color.b,
                'score' : int(player.score/100),
                'x' : int(player.x),
                'y' : int(player.y)
            } for player in self.players if player.is_connected
        }
        if current_state:
            self.server.network.send_all("game_update", current_state)
        for reception in self.server.network.last_receptions:
            if reception[pgg.HEADER] == 'new_player':
                if reception[pgg.ID] not in (playr.id for playr in self.players):
                    color = pgg.Color(reception[pgg.PAYLOAD]['red'], reception[pgg.PAYLOAD]['green'], reception[pgg.PAYLOAD]['blue'])
                    self.players.append(Player(reception[pgg.ID], color, reception[pgg.PAYLOAD]['name']))
                else:
                    player = [playr for playr in self.players if playr.id == reception[pgg.ID]][0]
                    color = pgg.Color(reception[pgg.PAYLOAD]['red'], reception[pgg.PAYLOAD]['green'], reception[pgg.PAYLOAD]['blue'])
                    player.rejoin(color, reception[pgg.PAYLOAD]['name'])

            elif reception[pgg.HEADER] == "action":
                player = [playr for playr in self.players if playr.id == reception[pgg.ID]][0]
                if reception[pgg.PAYLOAD] == "disconnection":
                    player.leave()
                
                elif reception[pgg.PAYLOAD] == "right":
                    player.turn(loop_duration, False, True)

                elif reception[pgg.PAYLOAD] == "left":
                    player.turn(loop_duration, True, False)

        for player in self.players:
            if player.is_connected:
                player.update(loop_duration)

    def start(self):
        pass

    def end(self):
        pass


serv = pgg.Server(15, 'game')
ServerPhase(serv)
serv.run()