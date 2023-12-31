import tkinter as tk
from tkinter import ttk
from utils.client_to_server_messages import create_lobby_joining_message


# Class that represent main Lobby window
class LobbyWindow:
    def __init__(self, parent, server):
        self.parent = parent
        self.lobby_listbox = None
        self.server = server
        self.chat_window = None
        self.connection_status_label = None
        self.connection_status_dot = None

    # Method that close whole app
    def on_closing(self):
        self.parent.destroy()

    # Method that opens lobby window
    def open_chat_window(self):
        self.chat_window = tk.Toplevel(self.parent)
        self.chat_window.title("Lobby Window")
        self.chat_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.lobby_listbox = tk.Listbox(self.chat_window)
        self.lobby_listbox.pack(pady=10, fill="both", expand=True)

        self.connection_status_label = ttk.Label(self.chat_window, text="Server Connection:")
        self.connection_status_label.pack(pady=5)

        self.connection_status_dot = ttk.Label(self.chat_window, width=2, background="green")
        self.connection_status_dot.pack(pady=5)

        self.lobby_listbox.bind("<Double-Button-1>", self.on_double_click)

    # Method that update lobby list
    def update_lobby_list(self, lobbies):
        self.lobby_listbox.delete(0, tk.END)

        for lobby in lobbies:
            lobby_name = lobby['nick']
            current_players = lobby['current_players']
            max_players = lobby['max_players']
            status = 'Waiting' if lobby['game_status'] == 1 else 'Started'
            lobby_info = f"{lobby_name} - {current_players}/{max_players} ({status})"
            self.lobby_listbox.insert(tk.END, lobby_info)

    # Event listener (double click listener) for item in list box
    def on_double_click(self, event):
        selected_index = self.lobby_listbox.curselection()
        if selected_index:
            selected_item = self.lobby_listbox.get(selected_index)
            lobby_name = self.extract_lobby_name(selected_item)
            message = create_lobby_joining_message(lobby_name)
            self.server.sendall((message + "\n").encode())

    # Method that extract lobby name
    def extract_lobby_name(self, lobby_info):
        lobby_name = lobby_info.split('-')[0].strip()
        return lobby_name

    # Method that close lobby window
    def close_lobby_window(self):
        self.chat_window.withdraw()

    # Method that updates connection status
    def update_connection_status(self, is_server_available):
        if self.connection_status_dot is not None and self.connection_status_dot.winfo_exists():
            color = "green" if is_server_available else "red"
            self.connection_status_dot.configure(background=color)

