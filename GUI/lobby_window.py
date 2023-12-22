
import tkinter as tk

class LobbyWindow:
    def __init__(self, parent, on_double_click_callback):
        self.parent = parent
        self.on_double_click_callback = on_double_click_callback

    def open_chat_window(self):
        chat_window = tk.Toplevel(self.parent)
        chat_window.title("Chat Window - ")

        lobby_listbox = tk.Listbox(chat_window)
        lobby_listbox.pack(pady=10, fill="both", expand=True)

        lobby_listbox.bind("<Double-Button-1>", self.on_double_click_callback)