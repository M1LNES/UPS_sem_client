import socket
import threading
import utils.client_to_server_messages as messageHandler
import utils.validation as validate
from tkinter import ttk
from constants import message_constants
from GUI.lobby_window import LobbyWindow
from GUI.game_window import GameWindow


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Window")

        self.server_ip_label = ttk.Label(root, text="Server IP:")
        self.server_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.server_ip_entry = ttk.Entry(root)
        self.server_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        self.server_port_label = ttk.Label(root, text="Server Port:")
        self.server_port_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.server_port_entry = ttk.Entry(root)
        self.server_port_entry.grid(row=1, column=1, padx=5, pady=5)

        self.nickname_label = ttk.Label(root, text="Nickname:")
        self.nickname_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.nickname_entry = ttk.Entry(root)
        self.nickname_entry.grid(row=2, column=1, padx=5, pady=5)

        self.connect_button = ttk.Button(root, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.server = None
        self.response_thread = None
        self.lobby_listbox = None
        self.lobby_window_initializer = None
        self.game_window_initializer = None

    def connect_to_server(self):
        ip = self.server_ip_entry.get()
        port = int(self.server_port_entry.get())
        nickname = self.nickname_entry.get()

        if not (validate.validate_name(nickname) and validate.validate_server_ip(ip) and validate.validate_port(port)):
            return

        message = messageHandler.create_nick_message(self.nickname_entry.get())

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((ip, port))

            self.response_thread = threading.Thread(target=self.handle_server_response)
            self.response_thread.start()

            self.open_chat_window(self.server)

            self.server.sendall((message + "\n").encode())

            self.root.withdraw()
        except Exception as e:
            print(f"Error connecting: {str(e)}")

    def open_chat_window(self, server):
        self.lobby_window_initializer = LobbyWindow(self.root, server)
        self.lobby_window_initializer.open_chat_window()

    def handle_server_response(self):
        while True:
            try:
                response = self.server.recv(1024).decode()
                self.handle_response_from_server(response)

                if not response:
                    print("Server disconnected.")
                    break

            except Exception as e:
                print(f"Error reading from server: {str(e)}")
                break

    def update_lobby_list(self, lobbies):
        self.lobby_window_initializer.update_lobby_list(lobbies)

    def handle_message(self, message):
        message_type = message[len(message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT:len(
            message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT + message_constants.MESSAGE_TYPE_LENGTH]
        message_body = message[len(
            message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT + message_constants.MESSAGE_TYPE_LENGTH:]
        if message_type == message_constants.LOBBY_INFO_TYPE:
            lobbies = messageHandler.extract_lobbies_info(message_body)
            self.update_lobby_list(lobbies)
        elif message_type == message_constants.LOBBY_JOIN_RESPONSE:
            success = messageHandler.joined_lobby_successfully(message_body)
            if success:
                self.lobby_window_initializer.close_lobby_window()
                self.game_window_initializer = GameWindow(self.root, self.server)
                self.game_window_initializer.open_game_window()
        elif message_type == message_constants.CAN_GAME_START:
            canBeStarted = messageHandler.can_game_begin(message_body)
            current_players, max_players = messageHandler.extract_players(message_body)

            self.game_window_initializer.current_players = current_players
            self.game_window_initializer.max_players = max_players

            if canBeStarted:
                self.game_window_initializer.can_be_started = True
            else:
                self.game_window_initializer.can_be_started = False
        elif message_type == message_constants.GAME_STARTED_INIT:
            self.game_window_initializer.extract_init_game_info(message_body)
    def handle_response_from_server(self, response):
        print("Server response: ", response)
        response = response.replace("\n", "")
        if messageHandler.is_message_valid(response):
            self.handle_message(response)
        else:
            print("Not valid")
        pass
