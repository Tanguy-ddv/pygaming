"""The server class is used to communicate with the clients."""

import socket
import threading
import json
import time
from pygame.time import get_ticks
from ..config import Config
from ._constants import DISCOVERY_PORT, TIMESTAMP, PAYLOAD, HEADER, NEW_ID, ONLINE, OFFLINE, BROADCAST_IP, IP, ID

class _ClientSocketManager:
    """
    This class is used to store the client socked object along with its id, address and port.

    Without this class, deconnection of players might create duplicate ids.
    """

    def __init__(self, client_socket: socket.socket, id_: int, address: str, port: int):
        """Create an instance of the clientSocket."""
        self.socket = client_socket
        self.id_ = id_
        self.status = ONLINE
        self.address = address
        self.port = port

class Server:
    """
    The server must be unique. It is launched with the server_main function.
    Every player, i.e. every client, connect to this server. This server receive and
    transmit the data to the players.
    
    Params:
    -----
    - config: the game config, used to get the hosrt port.
    - nb_max_players: int, the maximum number of players in one game.
    """
    def __init__(self, config: Config, nb_max_player: int = 8):

        self._host_ip = socket.gethostbyname(socket.gethostname())
        self._config = config

        self._nb_max_player = nb_max_player
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket_managers: list[_ClientSocketManager] = []
        self._running = True
        self._reception_buffer = []
        self.last_receptions = []
        print(f"Server launched: {self._host_ip}, {self._config.server_port}")
        self._server_socket.bind((self._host_ip, self._config.server_port))
        self._server_socket.listen(nb_max_player*2)
        threading.Thread(target=self._accept_clients).start()
        self._broadcasting = True
        threading.Thread(target=self._broadcast_address).start()

    def _accept_clients(self):
        """Accept a new client."""
        while self._running:
            try:
                client_socket, (address, port) = self._server_socket.accept()
                if address not in [client_socket_m.address for client_socket_m in self._client_socket_managers]:
                    if self._client_socket_managers:
                        id_ = max(client_socket_m.id_ for client_socket_m in self._client_socket_managers) +1
                    else:
                        id_ = 1
                    self._client_socket_managers.append(_ClientSocketManager(client_socket, id_, address, port))
                    print(f"New client connected: {address} has the id {id_}")
                else:
                    for client_socket_m in self._client_socket_managers:
                        if client_socket_m.address == address:
                            client_socket_m.status = ONLINE
                            client_socket_m.port = port
                            client_socket_m.socket = client_socket
                            print(f"Client {address} (id={id_}) is now reconnected")

                welcome_message = {HEADER : NEW_ID, PAYLOAD : id_}
                json_message = json.dumps(welcome_message) + self._config.get("network_sep")
                client_socket.send(json_message.encode())
                threading.Thread(target=self._handle_client, args=(client_socket, id_)).start()
            except OSError:
                print("Server disconnected.")
                self.stop()

    def _broadcast_address(self):
        """Send in the socket.SOCK_DGRAM socket the host_ip and the host port."""
        self._broadcasting = True
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = json.dumps({HEADER : BROADCAST_IP, PAYLOAD : {IP : self._host_ip, ID : self._config.get('game_id')}})
        pause_time = self._config.get("broadcast_period")/1000
        while self._running:
            if self._broadcasting and self.get_nb_players() < self._nb_max_player:
                broadcast_socket.sendto(message.encode(), ('<broadcast>', DISCOVERY_PORT))
            time.sleep(pause_time)  # Send broadcast every broadcast_frquency ms

    def start_broadcast(self):
        """Manually start the broadcast of the server ip."""
        self._broadcasting = True

    def stop_broadcast(self):
        """Manually stop the broadcast of the server ip."""
        self._broadcasting = False

    def _handle_client(self, client_socket: socket.socket, id_: int):
        while self._running:
            try:
                data = client_socket.recv(self._config.max_communication_length)
                if data:
                    try:
                        json_data = [json.loads(jdata) for jdata in data.decode().split(self._config.get("network_sep")) if jdata]
                        self._reception_buffer.extend(json_data)
                    except json.JSONDecodeError:
                        print(f"Unable to understand {data} as a data object.")
            except ConnectionError:
                for client_sck in self._client_socket_managers:
                    if client_sck.id_ == id_:
                        print(f"Client {client_sck.address} with id {client_sck.id_} just disconnected.")
                        client_sck.status = OFFLINE
                break

    def update(self) -> list[dict]:
        """Return the last data received."""
        self.last_receptions = self._reception_buffer.copy()
        self._reception_buffer.clear()

    def get_nb_players(self) -> int:
        """get the number of player connected to the server."""
        return len(list(filter(lambda csm: csm.status == ONLINE, self._client_socket_managers)))

    def is_player_online(self, id_) -> int:
        """Return True if the player with this id is currently online."""
        return len(list(filter(lambda csm: csm.status == ONLINE and csm.id_ == id_, self._client_socket_managers))) == 1

    def send(self, client_id, header, data):
        """The data to one client."""
        for client_socket in self._client_socket_managers:
            if client_socket.id_ == client_id:
                if client_socket.status == ONLINE:
                    try:
                        json_data: str = json.dumps({HEADER : header, PAYLOAD : data, TIMESTAMP : get_ticks()}) + self._config.get("network_sep")
                        client_socket.socket.send(json_data.encode("utf-8"))
                    except ConnectionResetError:
                        client_socket.status = OFFLINE
                    except Exception:
                        pass
                break

    def send_all(self, header, data):
        """Send data to all the clients."""
        for client_socket in self._client_socket_managers:
            if client_socket.status == ONLINE:
                try:
                    json_data: str = json.dumps({HEADER : header, PAYLOAD : data, TIMESTAMP : get_ticks()}) + self._config.get("network_sep")
                    client_socket.socket.send(json_data.encode("utf-8"))
                except ConnectionResetError:
                    client_socket.status = OFFLINE
                except Exception:
                    pass

    def stop(self):
        """Stop the server when the process is finished."""
        self._running = False
        self._server_socket.close()
        for client_socket in self._client_socket_managers:
            client_socket.socket.close()

    def __del__(self):
        self.stop()
