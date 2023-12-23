import tkinter as tk
from tkinter import ttk

class GameWindow:
    def __init__(self, parent, server):
        self.parent = parent
        self.game_window = None
        self.server = server
        self._can_be_started = False  # Use a private attribute with a leading underscore
        self._current_players = 0
        self._max_players = 0

    @property
    def can_be_started(self):
        return self._can_be_started

    @can_be_started.setter
    def can_be_started(self, value):
        if self._can_be_started != value:
            self._can_be_started = value
            self.refresh_gui()

    @property
    def current_players(self):
        return self._current_players

    @current_players.setter
    def current_players(self, value):
        if self._current_players != value:
            self._current_players = value
            self.refresh_gui()

    @property
    def max_players(self):
        return self._max_players

    @max_players.setter
    def max_players(self, value):
        if self._max_players != value:
            self._max_players = value
            self.refresh_gui()

    def open_game_window(self):
        self.game_window = tk.Toplevel(self.parent)
        self.game_window.title("Game Window")

        self.status_label = ttk.Label(self.game_window, text="Waiting for players")
        self.status_label.grid(row=0, column=0, pady=10)

        self.start_button = ttk.Button(self.game_window, text="Start the game", command=self.start_game)

        self.current_players_label = ttk.Label(self.game_window, text="Current Players:")
        self.current_players_label.grid(row=2, column=0, pady=5)

        self.refresh_gui()

    def start_game(self):
        self.can_be_started = not self.can_be_started

    def refresh_gui(self):
        if self.can_be_started:
            self.start_button.grid(row=1, column=0, pady=10)
        else:
            self.start_button.grid_forget()
        players_info = f"{self._current_players}/{self._max_players}"
        self.current_players_label.config(text=f"Current Players: {players_info}")
    def start_game(self):
        self.status_label.config(text="Game is in progress")