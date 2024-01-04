import socket
import threading
import time

import utils.client_to_server_messages as messageHandler
import utils.validation as validate
from tkinter import ttk
from constants import message_constants
from GUI.lobby_window import LobbyWindow
from GUI.game_window import GameWindow
from utils.validation import pop_alert_invalid_login_params, pop_alert_not_joined, pop_alert_connection_lost, \
    pop_alert_disconnected, pop_alert_already_in_game
from utils import validation

# Class that manages whole app and shows Login Window
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
        self.lock = threading.Lock()

    # Method for thread that check if connection is available
    def check_timeout(self):
        while not self.timer_stop_event.is_set():
            with self.lock:
                current_time = time.time()
                elapsed_time = current_time - self.last_message_time
                if elapsed_time >= self.timeout_duration:
                    if self.is_server_available:  # change of the state - connected -> not connected
                        pop_alert_connection_lost(self.root)
                    self.is_server_available = False
                else:
                    self.is_server_available = True
                if elapsed_time >= 30:
                    self.disconnect_from_server()
                    return

                self.update_children_state()

            time.sleep(2)

    # Method for connecting to the server
    def connect_to_server(self):
        ip = self.server_ip_entry.get()
        port = int(self.server_port_entry.get())
        nickname = self.nickname_entry.get()

        if not (validate.validate_name(nickname) and validate.validate_server_ip(ip) and validate.validate_port(port)):
            pop_alert_invalid_login_params(self.root)
            return
        self.player_nickname = nickname

        message = messageHandler.create_nick_message(self.nickname_entry.get())

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((ip, port))

            self.response_thread = threading.Thread(target=self.handle_server_response)
            self.response_thread.daemon = True
            self.response_thread.start()
            self.is_server_available = True
            self.open_chat_window(self.server)

            self.server.sendall((message + "\n").encode())
            self.last_message_time = time.time()
            self.timer_stop_event = threading.Event()
            self.timer_thread = threading.Thread(target=self.check_timeout)
            self.timer_thread.daemon = True
            self.timer_thread.start()

            self.root.withdraw()
        except Exception as e:
            pop_alert_not_joined(self.root)

    # Method that creates Login window
    def open_chat_window(self, server):
        self.lobby_window_initializer = LobbyWindow(self.root, server)
        self.lobby_window_initializer.open_chat_window()

    # Method that handles messages from server
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
                print(f"Error reading response from server, connection closed.")
                break

    # Method that calls method from child component to update lobbies
    def update_lobby_list(self, lobbies):
        self.lobby_window_initializer.update_lobby_list(lobbies)

    # Method that handle messages
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
            if not validation.validate_lobby_info_type(message_body):
                self.disconnect_from_server()
            lobbies = messageHandler.extract_lobbies_info(message_body)
            self.update_lobby_list(lobbies)
        elif message_type == message_constants.LOBBY_JOIN_RESPONSE:
            if not validation.validate_lobby_join_response(message_body):
                self.disconnect_from_server()
            success = messageHandler.joined_lobby_successfully(message_body)
            if success:
                self.lobby_window_initializer.close_lobby_window()
                self.game_window_initializer = GameWindow(self.root, self.server,
                                                          self.lobby_window_initializer.chat_window,
                                                          self.is_server_available)
                self.game_window_initializer.open_game_window()
        elif message_type == message_constants.CAN_GAME_START:
            if not validation.validate_can_game_start(message_body):
                self.disconnect_from_server()

            canBeStarted = messageHandler.can_game_begin(message_body)
            current_players, max_players = messageHandler.extract_players(message_body)

            self.game_window_initializer.current_players = current_players
            self.game_window_initializer.max_players = max_players
            self.game_window_initializer.can_be_started = canBeStarted

        elif message_type == message_constants.GAME_STARTED_INIT:
            if not validation.validate_game_started_init(message_body):
                self.disconnect_from_server()
            self.game_window_initializer.extract_init_game_info(message_body)
        elif message_type == message_constants.SENTENCE_GUESSED:
            if not validation.validate_setence_gussed(message_body):
                self.disconnect_from_server()
            self.game_window_initializer.show_guessed_sentence(message_body)
        elif message_type == message_constants.GAME_ENDING:
            if not validation.validate_game_ending(message_body):
                self.disconnect_from_server()
            self.game_window_initializer.end_the_game(message_body)
        elif message_type == message_constants.PING:
            self.send_pong()
        elif message_type == message_constants.CANCEL:
            self.game_window_initializer.cancel_game()
        elif message_type == message_constants.PENDING_USER:
            if not validation.validate_pending_user(message_body):
                self.disconnect_from_server()
            self.game_window_initializer.update_pending_users(message_body)
        elif message_type == message_constants.CONNECTED_USER:
            if not validation.validate_connected_user(message_body):
                self.disconnect_from_server()
            self.game_window_initializer.remove_pending_user(message_body)
        elif message_type == message_constants.LETTER_SELECTED:
            self.game_window_initializer.keyboard_frame.grid_forget()
        elif message_type == message_constants.RETRIEVING_STATE:
            if not validation.validate_retrieving_state(message_body):
                self.disconnect_from_server()
            self.game_window_initializer.retrieve_state(message_body)
        elif message_type == message_constants.ALREADY_IN_GAME:
            pop_alert_already_in_game(self.root)
        elif message_type == message_constants.ERROR:
            self.disconnect_from_server()
        elif message_type == message_constants.INFO:
            pass
        else:
            self.disconnect_from_server()

    # Method that handle response from server
    def handle_response_from_server(self, response):
        print("Server response: ", response)
        response = response.replace("\n", "")
        if messageHandler.is_message_valid(response):
            with self.lock:
                self.handle_message(response)
        else:
            self.disconnect_from_server()
        pass

    # Method that send pong message
    def send_pong(self):
        message = messageHandler.create_pong_message()
        self.server.sendall((message + "\n").encode())

    # Method that update connection status in child components
    def update_children_state(self):
        if self.game_window_initializer is not None:
            self.game_window_initializer.update_connection_status(self.is_server_available)
        if self.lobby_window_initializer is not None:
            self.lobby_window_initializer.update_connection_status(self.is_server_available)

    # Method that disconnect user from server and show login window with fulfilled params
    def disconnect_from_server(self):
        pop_alert_disconnected(self.root)
        self.lobby_window_initializer.chat_window.destroy()
        if self.game_window_initializer is not None:
            self.game_window_initializer.game_window.destroy()
        try:
            if self.server:
                self.server.close()
        except Exception as e:
            print(f"Error closing the socket: {e}")
        self.server = None
        self.root.deiconify()
        self.timer_stop_event.set()
