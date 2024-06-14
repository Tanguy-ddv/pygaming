"""The server class is used to communicate with the clients."""

import socket
import threading
import json

class ClientSocketManager():
    """
    This class is used to store the client socked object along with its id, address and port.

    Without this class, deconnection of players might create duplicate ids.
    """

    def __init__(self, client_socket: socket.socket, id_: int, address: str, port):
        """Create an instance of the clientSocket."""
        self.socket = client_socket
        self.id_ = id_
        self.status = 'online'
        self.address = address
        self.port = port

class Server:
    """
    The server must be unique. It is launched with the server_main function.
    Every player, i.e. every client, connect to this server. This server receive and
    transmit the data to the game.
    """
    def __init__(self, host_ip, host_port):

        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket_managers: list[ClientSocketManager] = []
        self.__running = True
        self.__last_received = {}
        self.__is_triggered = False
        print(f"Server launched: {host_ip}, {host_port}")
        self.__server_socket.bind((host_ip, host_port))
        self.__server_socket.listen(20)
        threading.Thread(target=self.__accept_clients).start()

    def __accept_clients(self):
        while self.__running:
            client_socket, (address, port) = self.__server_socket.accept()
            if address not in [client_socket_m.address for client_socket_m in self.__client_socket_managers]:
                if self.__client_socket_managers:
                    id_ = max(client_socket_m.id_ for client_socket_m in self.__client_socket_managers) +1
                else:
                    id_ = 1
                self.__client_socket_managers.append(ClientSocketManager(client_socket, id_, address, port))
                print(f"New client connected: {address} has the id {id_}")
            else:
                for client_socket_m in self.__client_socket_managers:
                    if client_socket_m.address == address:
                        client_socket_m.status == 'online'
                        client_socket_m.port = port
                        print(f"Client {address} (id={id_}) is now reconnected")

            welcome_message = {"header" : "new_id", "content" : id_}
            json_message = json.dumps(welcome_message)
            client_socket.send(json_message.encode())
            threading.Thread(target=self.__handle_client, args=(client_socket, id_)).start()

    def __handle_client(self, client_socket: socket.socket, id_: int):
        while self.__running:
            try:
                data = client_socket.recv(1024)
                if data:
                    json_data = json.loads(data.decode())
                    self.__last_received = json_data
                    self.__is_triggered = True
                else:
                    self.__is_triggered = False
            except Exception:
                for client_sck in self.__client_socket_managers:
                    if client_sck.id_ == id_:
                        print(f"Client {client_sck.address} with id {client_sck.id_} just deconnected.")
                        client_sck.status = 'offline'
                break
    
    def get_last_received(self) -> dict:
        """Return the last data received."""
        if self.__is_triggered:
            self.__is_triggered = False
            return self.__last_received

    def send(self, client_id, data):
        """The data to one client."""
        for client_socket in self.__client_socket_managers:
            if client_socket.id_ == client_id:
                json_data = json.dumps(data)
                client_socket.socket.send(json_data.encode())

    def send_all(self, data):
        """Send data to all the clients."""
        for client_socket in self.__client_socket_managers:
            json_data = json.dumps(data)
            client_socket.socket.send(json_data.encode())

    def stop(self):
        self.__running = False
        self.__server_socket.close()
        for client_socket in self.__client_socket_managers:
            client_socket.socket.close()

if __name__ == '__main__':
    SERVER_IP = socket.gethostbyname(socket.gethostname())
    print("The server's IP adress is:", SERVER_IP)
    SERVER_PORT = 50505
    server = Server(SERVER_IP, SERVER_PORT)
    while True:
        last_received = server.get_last_received()
        if last_received:
            print(last_received)