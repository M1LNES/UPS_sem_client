import tkinter as tk
from tkinter import ttk

class GameWindow:
    def __init__(self, parent, server):
        self.parent = parent
        self.game_window = None
        self.server = server

    def open_game_window(self):
        self.game_window = tk.Toplevel(self.parent)
        self.game_window.title("Game Window")

        self.status_label = ttk.Label(self.game_window, text="Waiting for players")
        self.status_label.pack(pady=10)

        self.start_button = ttk.Button(self.game_window, text="Start the game", command=self.start_game)
        self.start_button.pack(pady=10)

    def start_game(self):
        self.status_label.config(text="Game is in progress")
