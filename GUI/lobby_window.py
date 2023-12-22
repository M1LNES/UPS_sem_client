
import tkinter as tk

class LobbyWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Window - ")

        # Create the lobby listbox
        self.lobby_listbox = tk.Listbox(root)
        self.lobby_listbox.pack(pady=10, fill="both", expand=True)

    def update_lobby_list(self, lobbies):
        # Clear existing items in the listbox
        print("Lobbies: ", lobbies)
        self.lobby_listbox.delete(0, tk.END)

        # Insert new lobby information into the listbox
        for lobby in lobbies:
            lobby_info = f"{lobby['nick']} | Max Players: {lobby['max_players']} | Current Players: {lobby['current_players']} | Status: {'Waiting' if lobby['game_status'] == 1 else 'Started'}"
            self.lobby_listbox.insert(tk.END, lobby_info)
