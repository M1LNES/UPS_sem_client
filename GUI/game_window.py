import tkinter as tk
from tkinter import ttk
from utils.client_to_server_messages import create_start_game_message
from utils.client_to_server_messages import create_selected_letter_message
from utils.client_to_server_messages import create_resend_state_message
from constants import message_constants
from tkinter import messagebox


# Function that shows cancel alert
def show_info_message(info_message):
    messagebox.showinfo("Cancel Alert", info_message)


# Class that represents game window
class GameWindow:
    def __init__(self, parent, server, chat_window, is_server_available):
        self.parent = parent
        self.game_window = None
        self.server = server
        self._can_be_started = False
        self._current_players = 0
        self._max_players = 0
        self.nicknames = []
        self.points = {}
        self.unique_characters = ""
        self.masked_sentence = ""
        self.hint = ""
        self.game_started = False
        self.keyboard_frame = None
        self.game_gui_mounted = False
        self.buttons = []
        self.game_ended = False
        self.winners = []
        self.chat_window = chat_window
        self.round_over = False
        self.is_server_available = is_server_available
        self.status_label = None
        self.connection_dot = None
        self.connection_label = None
        self.pending_users = []

    # Method that update the rectangle symbolising (in)activity
    def update_connection_status(self, is_server_available):
        if self.connection_dot is not None and self.connection_dot.winfo_exists():
            color = "green" if is_server_available else "red"
            self.connection_dot.configure(background=color)

    # Getter for can_be_started attribute
    @property
    def can_be_started(self):
        return self._can_be_started

    # Setter for can_be_started attribute
    @can_be_started.setter
    def can_be_started(self, value):
        if self._can_be_started != value:
            self._can_be_started = value
            self.refresh_gui()

    # Getter for current_players attribute
    @property
    def current_players(self):
        return self._current_players

    # Setter for current_players attribute
    @current_players.setter
    def current_players(self, value):
        if self._current_players != value:
            self._current_players = value
            self.refresh_gui()

    # Getter for max_players attribute
    @property
    def max_players(self):
        return self._max_players

    # Setter for max_players attribute
    @max_players.setter
    def max_players(self, value):
        if self._max_players != value:
            self._max_players = value
            self.refresh_gui()

    # Method that destroys whole app
    def on_closing(self):
        self.parent.destroy()

    # Method that opens game window
    def open_game_window(self):
        self.game_window = tk.Toplevel(self.parent)
        self.game_window.title("Game Window")
        self.game_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.status_label = ttk.Label(self.game_window, text="Waiting for players")
        self.status_label.grid(row=0, column=0, pady=10)

        self.connection_label = ttk.Label(self.game_window, text="Server Connection:")
        self.connection_label.grid(row=1, column=0, pady=5)

        self.connection_dot = ttk.Label(self.game_window, width=2, background="green")
        self.connection_dot.grid(row=2, column=0, pady=5)

        self.start_button = ttk.Button(self.game_window, text="Start the game", command=self.start_game)

        self.current_players_label = ttk.Label(self.game_window, text="Current Players:")
        self.current_players_label.grid(row=4, column=0, pady=5)

        self.refresh_gui()

    # Method that refresh GUI
    def refresh_gui(self):
        if self.game_ended:
            self.update_climbers()
            self.show_final_panel()
        elif self.can_be_started and not self.game_started:
            self.start_button.grid(row=3, column=0, pady=10)
            self.actualize_current_players_label()
        elif self.game_started:
            self.initialize_game()
            self.update_climbers()
        else:
            self.actualize_current_players_label()

    # Method that actualize label of current players
    def actualize_current_players_label(self):
        players_info = f"{self._current_players}/{self._max_players}"
        self.current_players_label.config(text=f"Current Players: {players_info}")

    # Method that send message to server to start the game
    def start_game(self):
        message = create_start_game_message()
        self.server.sendall((message + "\n").encode())

    # Method that extract info about current game state
    def extract_init_game_info(self, message_body):
        self.game_started = True
        segments = message_body.split('|')

        if len(segments) == 4:
            player_info = segments[0].split(';')
            self.nicknames = []
            self.points = {}

            for player_data in player_info:
                player_data_parts = player_data.split(':')
                if len(player_data_parts) == 2:
                    nickname, points_str = player_data_parts
                    self.nicknames.append(nickname)
                    self.points[nickname] = int(points_str)

            self.unique_characters = segments[1]
            self.masked_sentence = segments[2]
            self.hint = segments[3]
            self.refresh_gui()
        else:
            return None

    # Method that prints window
    def initialize_game(self):
        if not self.game_gui_mounted:
            self.status_label.config(text="Game started")

            self.nicknames_label = ttk.Label(self.game_window, text="Nicknames:")
            self.nicknames_label.grid(row=7, column=0, pady=5)

            self.unique_characters_label = ttk.Label(self.game_window, text="Selected Characters:")
            self.unique_characters_label.grid(row=5, column=0, pady=5)

            self.masked_sentence_label = ttk.Label(self.game_window, text="Masked Sentence:")
            self.masked_sentence_label.grid(row=6, column=0, pady=5)

            self.hint_label = ttk.Label(self.game_window, text="HINT::")
            self.hint_label.grid(row=8, column=0, pady=5)

            self.climbers_frame = ttk.Frame(self.game_window)
            self.climbers_frame.grid(row=10, column=0, pady=10)

            self.mountain_canvas = tk.Canvas(self.climbers_frame, width=600, height=200, bg="grey")
            self.mountain_canvas.pack()

            self.climbers = []

            self.start_button.grid_forget()

            self.game_gui_mounted = True

        players_info = f"{self._current_players}/{self._max_players}"
        active_players = [f"{nickname}: {self.points[nickname]}" for nickname in self.nicknames if
                          nickname not in self.pending_users]
        pending_players = [f"[Lost Connection] {nickname}: {self.points[nickname]}" for nickname in
                           self.pending_users]

        all_players = active_players + pending_players
        points_str = ", ".join(all_players)

        self.nicknames_label.config(text=f"Nicknames and Points: {points_str}")
        self.current_players_label.config(text=f"Current Players: {players_info}")

        self.unique_characters_label.config(text=f"Selected Characters:\n {self.unique_characters}",
                                            font=("Courier", 10), anchor="center", justify="center", )
        formatted_masked_sentence = " ".join(list(self.masked_sentence))
        self.masked_sentence_label.config(text=f"Masked Sentence:\n {formatted_masked_sentence}", font=("Courier", 14),
                                          anchor="center", justify="center", )
        self.hint_label.config(text=f"Hint:\n {self.hint}", font=("Courier", 12), anchor="center", justify="center", )

        # Clear existing buttons
        for button in self.buttons:
            button.destroy()

        if not self.round_over:
            self.keyboard_frame = ttk.Frame(self.game_window)
            self.keyboard_frame.grid(row=9, column=0, pady=10)

            keyboard_layout = [
                'QWERTYUIOP',
                'ASDFGHJKL',
                'ZXCVBNM'
            ]

            self.buttons = []

            for i, row in enumerate(keyboard_layout):
                for j, key in enumerate(row):
                    button = self.create_button(key, i + 6, j + 1)
        else:
            self.round_over = False

    # Method that create button with listener
    def create_button(self, key, row, col):
        button = tk.Button(self.keyboard_frame, text=key, width=5, height=2, command=lambda: self.button_click(key),
                           disabledforeground="red")

        if key.lower() in self.unique_characters:
            button.config(state=tk.DISABLED)

        button.grid(row=row, column=col, padx=1, pady=1)
        return button

    # Listener for buttons
    def button_click(self, key):
        # self.keyboard_frame.grid_forget()
        message = create_selected_letter_message(key)
        self.server.sendall((message + "\n").encode())

    # Method that informs user about guessing whole sentence
    def show_guessed_sentence(self, message_body):
        segments = message_body.split("|")

        if len(segments) == 3:
            player_info = segments[2].split(";")

            self.nicknames = []
            self.points = {}

            for player_data in player_info:
                player_data_parts = player_data.split(':')
                if len(player_data_parts) == 2:
                    nickname, points_str = player_data_parts
                    self.nicknames.append(nickname)
                    self.points[nickname] = int(points_str)

            self.masked_sentence = segments[1]
            self.hint = segments[0]
            self.round_over = True
            self.refresh_gui()
            self.pop_alert()

        else:
            print("Invalid message format")

    # Method that informs user about ending game
    def end_the_game(self, message_body):
        nicknames = message_body.split(";")
        self.winners = nicknames
        self.game_ended = True
        self.refresh_gui()

    # Method that shows final panel after ending the game
    def show_final_panel(self):
        if len(self.winners) > 1:
            self.unique_characters_label.config(text="WINNERS:" + ";".join(self.winners))
        else:
            self.unique_characters_label.config(text="WINNER:" + self.winners[0])
        self.status_label.config(text="GAME OVER")
        self.hint_label.config(text="Thanks for playing!")
        self.masked_sentence_label.config(text="Soon you will be moved back to the main lobby!")
        self.nicknames_label.config(text="")
        self.game_window.after(10000, self.close_window)
        # self.chat_window.deiconify()

    # Method that close game window and lobby window appear
    def close_window(self):
        self.game_window.destroy()
        self.chat_window.deiconify()

    # Method that repaints climbers
    def update_climbers(self):
        self.mountain_canvas.delete("all")

        for index, (nickname, points) in enumerate(self.points.items()):
            self.draw_climber(nickname, points, index)

    def draw_climber(self, nickname, points, index):
        base_x_position = 20
        x_position = self.calculate_x_position(index, len(self.nicknames))
        y_position = 200 - (points * 200 / message_constants.POINTS_TO_WIN)

        climber = self.mountain_canvas.create_rectangle(
            x_position, y_position, x_position + 20, y_position + 20, fill="blue", outline="black"
        )
        self.climbers.append(climber)

        nickname_text = self.mountain_canvas.create_text(
            x_position + 10, y_position - 10, text=nickname, fill="white")
        self.climbers.append(nickname_text)

    # Method that calculates position of climbers
    def calculate_x_position(self, index, total_climbers):
        base_x_position = 50
        mountain_width = 600
        available_width = mountain_width - 2 * base_x_position
        section_width = available_width / total_climbers
        x_position = base_x_position + index * section_width

        return x_position

    # Method that pop alert after round (guessing sentence)
    def pop_alert(self):
        info_message = (
            f"ROUND OVER - sentence guessed\n"
            f"Guessed, the sentence was: {self.masked_sentence}\n"
            f"Hint of the sentence was: {self.hint}\n\n"
            f"Player Points:\n"
        )

        for nickname in self.nicknames:
            info_message += f"{nickname}: {self.points.get(nickname, 0)} points\n"

        # Create a Toplevel window for the alert
        alert_window = tk.Toplevel(self.parent)
        alert_window.title("Game Alert")

        label = ttk.Label(alert_window, text=info_message)
        label.pack(padx=10, pady=10)

    # Method that pop alert informing users about inactivity of one of the users
    def pop_cancel_alert(self):
        info_message = (
            f"One of the players left\n"
            f"We are sorry but we must cancel this game\n"
            f"Moving back to the main lobby\n\n"
            f"Thanks for playing.\n"
        )

        cancel_alert_window = tk.Toplevel(self.parent)
        cancel_alert_window.title("Cancel Alert")

        label = ttk.Label(cancel_alert_window, text=info_message)
        label.pack(padx=10, pady=10)

    # Method for canceling game
    def cancel_game(self):
        self.pop_cancel_alert()
        self.close_window()

    # Method that update label of (in)active users
    def update_pending_users(self, pending_user):
        if pending_user not in self.pending_users:
            self.pending_users.append(pending_user)
            active_players = [f"{nickname}: {self.points[nickname]}" for nickname in self.nicknames if
                              nickname not in self.pending_users]
            pending_players = [f"[Lost Connection] {nickname}: {self.points[nickname]}" for nickname in
                               self.pending_users]

            all_players = active_players + pending_players
            points_str = ", ".join(all_players)

            self.nicknames_label.config(text=f"Nicknames and Points: {points_str}")

    # Method that removes pending user
    def remove_pending_user(self, user):
        if user in self.pending_users:
            self.pending_users.remove(user)
            active_players = [f"{nickname}: {self.points[nickname]}" for nickname in self.nicknames if
                              nickname not in self.pending_users]
            pending_players = [f"[Lost Connection] {nickname}: {self.points[nickname]}" for nickname in
                               self.pending_users]

            all_players = active_players + pending_players
            points_str = ", ".join(all_players)

            self.nicknames_label.config(text=f"Nicknames and Points: {points_str}")

    # Method that requires state refreshing
    def resend_state(self):
        message = create_resend_state_message()
        self.server.sendall((message + "\n").encode())

    # Method that retrieve state after disconnecting
    def retrieve_state(self, message_body):
        self.game_started = True
        segments = message_body.split('|')

        if len(segments) == 5:
            player_info = segments[0].split(';')
            self.nicknames = []
            self.points = {}

            for player_data in player_info:
                player_data_parts = player_data.split(':')
                if len(player_data_parts) == 2:
                    nickname, points_str = player_data_parts
                    self.nicknames.append(nickname)
                    self.points[nickname] = int(points_str)

            self.unique_characters = segments[1]
            self.masked_sentence = segments[2]
            self.hint = segments[3]
            self.refresh_gui()
            if segments[4] == "1":
                self.keyboard_frame.grid_forget()
        else:
            return None
