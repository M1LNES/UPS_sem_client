import tkinter as tk
from tkinter import ttk
from utils.client_to_server_messages import create_start_game_message
from utils.client_to_server_messages import create_selected_letter_message

class GameWindow:
    def __init__(self, parent, server):
        self.parent = parent
        self.game_window = None
        self.server = server
        self._can_be_started = False  # Use a private attribute with a leading underscore
        self._current_players = 0
        self._max_players = 0
        self.nicknames = []
        self.unique_characters = ""
        self.masked_sentence = ""
        self.game_started = False
        self.keyboard_frame = None

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

    def refresh_gui(self):
        if self.can_be_started and not self.game_started:
            self.start_button.grid(row=1, column=0, pady=10)
            self.actualize_current_players_label()
        elif self.game_started:
            self.initialize_game()
        else:
            self.actualize_current_players_label()


    def actualize_current_players_label(self):
        players_info = f"{self._current_players}/{self._max_players}"
        self.current_players_label.config(text=f"Current Players: {players_info}")

    def start_game(self):
        message = create_start_game_message()
        self.server.sendall((message + "\n").encode())

    def extract_init_game_info(self, message_body):
        self.game_started = True
        segments = message_body.split('|')

        if len(segments) == 3:
            self.nicknames = segments[0].split(';')
            self.unique_characters = segments[1]
            self.masked_sentence = segments[2]

            self.refresh_gui()
        else:
            return None

    def initialize_game(self):
        self.nicknames_label = ttk.Label(self.game_window, text="Nicknames:")
        self.nicknames_label.grid(row=5, column=0, pady=5)

        self.unique_characters_label = ttk.Label(self.game_window, text="Unique Characters:")
        self.unique_characters_label.grid(row=3, column=0, pady=5)

        self.masked_sentence_label = ttk.Label(self.game_window, text="Masked Sentence:")
        self.masked_sentence_label.grid(row=4, column=0, pady=5)

        self.start_button.grid_forget()
        players_info = f"{self._current_players}/{self._max_players}"
        self.current_players_label.config(text=f"Current Players: {players_info}")

        nicknames_str = ", ".join(self.nicknames)
        self.nicknames_label.config(text=f"Nicknames: {nicknames_str}")
        self.unique_characters_label.config(text=f"Unique Characters: {self.unique_characters}")
        self.masked_sentence_label.config(text=f"Masked Sentence: {self.masked_sentence}")

        self.keyboard_frame = ttk.Frame(self.game_window)
        self.keyboard_frame.grid(row=6, column=0, pady=10)

        keyboard_layout = [
            'QWERTYUIOP',
            'ASDFGHJKL',
            'ZXCVBNM'
        ]

        self.buttons = []

        for i, row in enumerate(keyboard_layout):
            for j, key in enumerate(row):
                button = self.create_button(key, i + 6, j+1)
                self.buttons.append(button)

    def create_button(self, key, row, col):
        button = tk.Button(self.keyboard_frame, text=key, width=5, height=2, command=lambda: self.button_click(key),
                           disabledforeground="red")

        if key.lower() in self.unique_characters:
            button.config(state=tk.DISABLED)

        button.grid(row=row, column=col, padx=1, pady=1)
        return button

    def button_click(self, key):
        self.keyboard_frame.grid_forget()
        message = create_selected_letter_message(key)
        self.server.sendall((message + "\n").encode())


