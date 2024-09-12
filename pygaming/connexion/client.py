"""The client class is used to communicate with the server."""

import socket
import threading
import json
import time
from typing import Any
from ._constants import MAX_COMMUNICATION_LENGTH, DISCOVERY_PORT, CONTENT, HEADER, ID, NEW_ID, SERVER_PORT, BROADCAST_IP, TIMESTAMP, EXIT, TIMESTAMP

class Client:
    """The Client instance is used to communicate with the server. It sends data via the .send()"""
    def __init__(self):
        self.last_received = {}
        self.id = None
        server_ip = self._discover_server()
        self._connect_to_server(server_ip)

    def send(self, header: str, content: Any, ):
        """Send the content to the server, specifying the header."""
        message = {ID : self.id, HEADER : header, CONTENT : content, TIMESTAMP : time.time()}
        json_data = json.dumps(message)
        self.client_socket.send(json_data.encode())

    def _discover_server(self):
        """use the SOCK_DGRAM socket to discover the server ip"""
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        discovery_socket.bind(('', DISCOVERY_PORT))
        while True:
            data, addr = discovery_socket.recvfrom(MAX_COMMUNICATION_LENGTH)
            message = json.loads(data.decode())
            if HEADER not in message or message[HEADER] != BROADCAST_IP:
                continue
            server_ip = message[CONTENT]
            discovery_socket.close()
            return server_ip
    
    def _connect_to_server(self, server_ip):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, SERVER_PORT))
        threading.Thread(target=self._receive).start()

    def _receive(self):
        while True:
            try:
                data = self.client_socket.recv(MAX_COMMUNICATION_LENGTH)
                if data:
                    json_data = json.loads(data.decode())
                    if json_data[HEADER] == NEW_ID:
                        self.id = json_data[CONTENT]
                    self.last_received = json_data
            except Exception:
                self.close()
                break

    def close(self):
        self.last_received = {HEADER : EXIT}
        self.client_socket.close()

    def clean_last(self):
        """Clean the reception."""
        self.last_received = {}
    
    @property
    def last_header(self):
        if HEADER in self.last_received:
            return self.last_received[HEADER]
    
    @property
    def last_content(self):
        if CONTENT in self.last_received:
            return self.last_received[CONTENT]
    
    @property
    def last_timestamp(self):
        if TIMESTAMP in self.last_received:
            return self.last_received[TIMESTAMP]

    def __del__(self):
        self.close()

if __name__ == '__main__':
    client = Client()

    for i in range(5):
        message = input("Enter message to send to server: ")
        client.send(header='test', content=message)
    client.close()