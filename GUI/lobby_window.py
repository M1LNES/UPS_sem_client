import tkinter as tk
from utils.client_to_server_messages import create_lobby_joining_message

class LobbyWindow:
    def __init__(self, parent, server):
        self.parent = parent
        self.lobby_listbox = None
        self.server = server

    def open_chat_window(self):
        chat_window = tk.Toplevel(self.parent)
        chat_window.title("Lobby Window")

        self.lobby_listbox = tk.Listbox(chat_window)
        self.lobby_listbox.pack(pady=10, fill="both", expand=True)

        self.lobby_listbox.bind("<Double-Button-1>", self.on_double_click)

    def update_lobby_list(self, lobbies):
        self.lobby_listbox.delete(0, tk.END)

        for lobby in lobbies:
            lobby_name = lobby['nick']
            current_players = lobby['current_players']
            max_players = lobby['max_players']
            status = 'Waiting' if lobby['game_status'] == 1 else 'Started'
            lobby_info = f"{lobby_name} - {current_players}/{max_players} ({status})"
            self.lobby_listbox.insert(tk.END, lobby_info)

    def on_double_click(self, event):
        selected_index = self.lobby_listbox.curselection()
        if selected_index:
            selected_item = self.lobby_listbox.get(selected_index)
            lobby_name = self.extract_lobby_name(selected_item)
            message = create_lobby_joining_message(lobby_name)
            self.server.sendall((message + "\n").encode())



    def extract_lobby_name(self, lobby_info):
        lobby_name = lobby_info.split('-')[0].strip()
        return lobby_name
