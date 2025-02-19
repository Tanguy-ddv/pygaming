"""The client class is used to communicate with the server."""

import socket
import threading
import json
from typing import Any
from pygame.time import get_ticks
from ._constants import DISCOVERY_PORT, PAYLOAD, HEADER, ID, NEW_ID, BROADCAST_IP, TIMESTAMP, EXIT, IP
from ..config import Config
from ..logger import Logger

class Client:
    """The Client instance is used to communicate with the server. It sends data via the .send()"""
    def __init__(self, config: Config, logger: Logger, initial_header: str = None, initial_payload: str = None):
        self._logger = logger
        self._config = config
        self._reception_buffer = []
        self.last_receptions = []
        self._running = True
        server_ip = self._discover_server()
        self.is_connected = bool(server_ip)
        if self.is_connected:
            self.is_connected = self._connect_to_server(server_ip)
            if initial_header and initial_payload:
                self.send(initial_header, initial_payload)
        else:
            self.client_socket = None # This happens when nothing is broadcasted.

    def send(self, header: str, payload: Any):
        """Send the payload to the server, specifying the header."""
        message = {ID : self.id, HEADER : header, PAYLOAD : payload, TIMESTAMP : get_ticks()}
        json_data = json.dumps(message) + self._config.get("network_sep")
        self.client_socket.send(json_data.encode())

    def _discover_server(self):
        """use the SOCK_DGRAM socket to discover the server ip"""
        discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        discovery_socket.bind(('', DISCOVERY_PORT))
        discovery_socket.settimeout(self._config.timeout/1000)
        while self._running:
            try:
                data = discovery_socket.recv(self._config.max_communication_length)
                message = json.loads(data.decode())
                if HEADER not in message or message[HEADER] != BROADCAST_IP or message[PAYLOAD][ID] != self._config.get('game_id'):
                    continue
                server_ip = message[PAYLOAD][IP]
                discovery_socket.close()
                return server_ip
            except socket.timeout:
                discovery_socket.close()
                return None

    def _connect_to_server(self, server_ip):
        # create the socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, self._config.server_port))
        self.client_socket.settimeout(self._config.timeout/1000)
        # start receiving data
        threading.Thread(target=self._receive).start()
        # wait for the welcome message to come.
        connected = False
        try:
            while self._running and not connected:
                for reception in self._reception_buffer:
                    if reception[HEADER] == NEW_ID:
                        self.id = reception[PAYLOAD]
                        connected = True

        except socket.timeout:
            self.client_socket.close()
        else:
            self.client_socket.settimeout(None)

        return connected

    def _receive(self):
        string_buffer = ""
        while self._running:
            try:
                data = self.client_socket.recv(self._config.max_communication_length)
                if data:
                    string_buffer += data.decode("utf-8")
                    splitted_buffer = string_buffer.split(self._config.get("network_sep"))
                    for jdata in splitted_buffer[:-1]:
                        if jdata:
                            try:
                                json_data = json.loads(jdata)
                            except json.JSONDecodeError:
                                # if a non json object is read from buffer, we log it case of debugging.
                                self._logger.write({"NetworkReadingError" : jdata}, True)
                            else:
                                self._reception_buffer.append(json_data)
                        string_buffer = splitted_buffer[-1]
            except ConnectionError:
                self.close()
                break

    def close(self):
        """Close the client at the end of the process."""
        self._reception_buffer = [{HEADER : EXIT}]
        self._running = False
        if self.client_socket is not None:
            self.client_socket.close()
        self.is_connected = False

    def clean_last(self):
        """Clean the reception."""
        self._reception_buffer = []

    def is_server_killed(self):
        """Verify if the server sent EXIT because it is killed."""
        return any(lr[HEADER] == EXIT for lr in self.last_receptions)

    def update(self):
        """Update the client every iteration with the last receptions."""
        self.last_receptions = self._reception_buffer.copy()
        self._reception_buffer.clear()

    def __del__(self):
        self.close()
