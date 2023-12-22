import socket
import threading
import tkinter as tk
import utils.client_to_server_messages as messageHandler
import utils.validation as validate
from tkinter import ttk
from constants import message_constants
from GUI.lobby_window import LobbyWindow
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

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

    def connect_to_server(self):
        ip = self.server_ip_entry.get()
        port = int(self.server_port_entry.get())
        nickname = messageHandler.create_message(self.nickname_entry.get())

        if not (validate.validate_name(nickname) and validate.validate_server_ip(ip) and validate.validate_port(port)):
            return

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((ip, port))

            self.response_thread = threading.Thread(target=self.handle_server_response)
            self.response_thread.start()

            # Send nickname to the server
            self.server.sendall((nickname + "\n").encode())

            # Open a new window for the chat
            self.open_chat_window()

            # Close the initial login window
            self.root.withdraw()  # Hide the window instead of destroying it
        except Exception as e:
            print(f"Error connecting: {str(e)}")

    def open_chat_window(self):
        print("Oteviram okno")
        chat_window = tk.Toplevel()
        chat_window.title(f"Chat Window - ")

        self.lobby_listbox = tk.Listbox(chat_window)
        self.lobby_listbox.pack(pady=10, fill="both", expand=True)

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
        # Clear existing items in the listbox
        print("Lobbies: ", lobbies)
        self.lobby_listbox.delete(0, tk.END)

        # Insert new lobby information into the listbox
        for lobby in lobbies:
            lobby_info = f"{lobby['nick']} | Max Players: {lobby['max_players']} | Current Players: {lobby['current_players']} | Status: {'Waiting' if lobby['game_status'] == 1 else 'Started'}"
            self.lobby_listbox.insert(tk.END, lobby_info)
    def handle_message(self,message):
        print("Handluju message")

        message_type = message[len(message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT:len(
            message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT + message_constants.MESSAGE_TYPE_LENGTH]
        message_body = message[len(
            message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT + message_constants.MESSAGE_TYPE_LENGTH:]
        if message_type == message_constants.LOBBY_INFO_TYPE:
            lobbies = messageHandler.extract_lobbies_info(message_body)
            print("Updatuju lobby")
            self.update_lobby_list(lobbies)



    def handle_response_from_server(self,response):
        response = response.replace("\n", "")
        if messageHandler.is_message_valid(response):
            self.handle_message(response)
        else:
            print("Not valid")
        pass
