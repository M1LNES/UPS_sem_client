import socket
import threading
import time

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
        self.buffer = b''
        self.timeout_duration = 6
        self.last_message_time = None
        self.timer_thread = None
        self.timer_stop_event = None
        self.is_server_available = False
        self.player_nickname = None


    def check_timeout(self):
        while not self.timer_stop_event.is_set():
            current_time = time.time()
            elapsed_time = current_time - self.last_message_time
            if elapsed_time >= self.timeout_duration:
                if self.is_server_available:  # change of the state - connected -> not connected
                    print("Lost connection to the server.")
                self.is_server_available = False
            else:
                self.is_server_available = True
            if elapsed_time >= 50:
                print("Vypinam a davam login obrazovku.")
                self.lobby_window_initializer.chat_window.destroy()
                if self.game_window_initializer is not None:
                    self.game_window_initializer.game_window.destroy()
                self.server.close()
                self.server = None
                self.root.deiconify()
                self.timer_stop_event.set()
                return

            self.update_children_state()
            time.sleep(2)
    def connect_to_server(self):
        ip = self.server_ip_entry.get()
        port = int(self.server_port_entry.get())
        nickname = self.nickname_entry.get()

        if not (validate.validate_name(nickname) and validate.validate_server_ip(ip) and validate.validate_port(port)):
            return
        self.player_nickname = nickname

        message = messageHandler.create_nick_message(self.nickname_entry.get())

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((ip, port))

            self.response_thread = threading.Thread(target=self.handle_server_response)
            self.response_thread.start()
            self.is_server_available = True
            self.open_chat_window(self.server)

            self.server.sendall((message + "\n").encode())
            self.last_message_time = time.time()
            self.timer_stop_event = threading.Event()
            self.timer_thread = threading.Thread(target=self.check_timeout)
            self.timer_thread.start()

            self.root.withdraw()
        except Exception as e:
            print(f"Error connecting: {str(e)}")

    def open_chat_window(self, server):
        self.lobby_window_initializer = LobbyWindow(self.root, server)
        self.lobby_window_initializer.open_chat_window()

    def handle_server_response(self):
        while True:
            try:
                data = self.server.recv(1024)
                if not data:
                    print("Server has disconnected.")
                    break

                self.buffer += data

                messages = self.buffer.split(b'\n')
                self.buffer = messages.pop()

                for msg in messages:
                    msg = msg.decode()
                    self.handle_response_from_server(msg)

            except Exception as e:
                print(f"Error reading response from server: {str(e)}")
                break

    def update_lobby_list(self, lobbies):
        self.lobby_window_initializer.update_lobby_list(lobbies)

    def handle_message(self, message):
        self.last_message_time = time.time()
        if not self.is_server_available:
            if self.game_window_initializer is not None:
                self.game_window_initializer.resend_state()
        self.is_server_available = True

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
                self.game_window_initializer = GameWindow(self.root, self.server,
                                                          self.lobby_window_initializer.chat_window,
                                                          self.is_server_available)
                self.game_window_initializer.open_game_window()
        elif message_type == message_constants.CAN_GAME_START:
            canBeStarted = messageHandler.can_game_begin(message_body)
            current_players, max_players = messageHandler.extract_players(message_body)

            self.game_window_initializer.current_players = current_players
            self.game_window_initializer.max_players = max_players
            self.game_window_initializer.can_be_started = canBeStarted

        elif message_type == message_constants.GAME_STARTED_INIT:
            self.game_window_initializer.extract_init_game_info(message_body)
        elif message_type == message_constants.SENTENCE_GUESSED:
            self.game_window_initializer.show_guessed_sentence(message_body)
        elif message_type == message_constants.GAME_ENDING:
            self.game_window_initializer.end_the_game(message_body)
        elif message_type == message_constants.PING:
            self.send_pong()
        elif message_type == message_constants.CANCEL:
            self.game_window_initializer.cancel_game()
        elif message_type == message_constants.PENDING_USER:
            self.game_window_initializer.update_pending_users(message_body)
        elif message_type == message_constants.CONNECTED_USER:
            self.game_window_initializer.remove_pending_user(message_body)
        elif message_type == message_constants.LETTER_SELECTED:
            self.game_window_initializer.keyboard_frame.grid_forget()
        elif message_type == message_constants.RETRIEVING_STATE:
            print("Prisla mi zadost o obnoveni stavu")

    def handle_response_from_server(self, response):
        print("Server response: ", response)
        response = response.replace("\n", "")
        if messageHandler.is_message_valid(response):
            self.handle_message(response)
        else:
            print("Not valid")
        pass

    def send_pong(self):
        message = messageHandler.create_pong_message()
        self.server.sendall((message + "\n").encode())

    def update_children_state(self):
        if self.game_window_initializer is not None:
            self.game_window_initializer.update_connection_status(self.is_server_available)
        if self.lobby_window_initializer is not None:
            self.lobby_window_initializer.update_connection_status(self.is_server_available)
