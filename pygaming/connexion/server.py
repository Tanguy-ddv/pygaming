"""The server class is used to communicate with the clients."""

import socket
import threading
import json
import time
from ._constants import SERVER_PORT, DISCOVERY_PORT, MAX_COMMUNICATION_LENGTH,  CONTENT, HEADER, NEW_ID, ONLINE, OFFLINE, BROADCAST_IP

class ClientSocketManager():
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
    """
    def __init__(self):

        host_ip = socket.gethostbyname(socket.gethostname())
        host_port = SERVER_PORT

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket_managers: list[ClientSocketManager] = []
        self._running = True
        self._last_received = []
        self._is_triggered = False
        print(f"Server launched: {host_ip}, {host_port}")
        self._server_socket.bind((host_ip, host_port))
        self._server_socket.listen(20)
        threading.Thread(target=self._accept_clients).start()
        threading.Thread(target=self._broadcast_address, kwargs={'host_port' : host_port, 'host_ip' : host_ip}).start()

    def _accept_clients(self):
        """Accept a new client."""
        while self._running:
            client_socket, (address, port) = self._server_socket.accept()
            if address not in [client_socket_m.address for client_socket_m in self._client_socket_managers]:
                if self._client_socket_managers:
                    id_ = max(client_socket_m.id_ for client_socket_m in self._client_socket_managers) +1
                else:
                    id_ = 1
                self._client_socket_managers.append(ClientSocketManager(client_socket, id_, address, port))
                print(f"New client connected: {address} has the id {id_}")
            else:
                for client_socket_m in self._client_socket_managers:
                    if client_socket_m.address == address:
                        client_socket_m.status == ONLINE
                        client_socket_m.port = port
                        print(f"Client {address} (id={id_}) is now reconnected")

            welcome_message = {HEADER : NEW_ID, CONTENT : id_}
            json_message = json.dumps(welcome_message)
            client_socket.send(json_message.encode())
            threading.Thread(target=self._handle_client, args=(client_socket, id_)).start()

    def _broadcast_address(self, host_ip):
        """Send in the socket.SOCK_DGRAM socket the host_ip and the host port every 5 seconds."""
        while self._running:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = json.dumps({HEADER : BROADCAST_IP, CONTENT:  host_ip})
            broadcast_socket.sendto(message.encode(), ('<broadcast>', DISCOVERY_PORT))
            time.sleep(5)  # Send broadcast every 5 seconds

    def _handle_client(self, client_socket: socket.socket, id_: int):
        while self._running:
            try:
                data = client_socket.recv(MAX_COMMUNICATION_LENGTH)
                if data:
                    json_data = json.loads(data.decode())
                    self._last_received.append(json_data)
            except Exception:
                for client_sck in self._client_socket_managers:
                    if client_sck.id_ == id_:
                        print(f"Client {client_sck.address} with id {client_sck.id_} just deconnected.")
                        client_sck.status = OFFLINE
                break
    
    def get_last_receptions(self) -> dict:
        """Return the last data received."""
        last_receiptions = self._last_received
        self._last_received.clear()
        return last_receiptions

    def send(self, client_id, data):
        """The data to one client."""
        for client_socket in self._client_socket_managers:
            if client_socket.id_ == client_id:
                json_data = json.dumps(data)
                client_socket.socket.send(json_data.encode())

    def send_all(self, data):
        """Send data to all the clients."""
        for client_socket in self._client_socket_managers:
            json_data = json.dumps(data)
            client_socket.socket.send(json_data.encode())

    def stop(self):
        self._running = False
        self._server_socket.close()
        for client_socket in self._client_socket_managers:
            client_socket.socket.close()

if __name__ == '__main__':
    server = Server()
    while True:
        last_received = server.get_last_receptions()
        for data in last_received:
            print(data)