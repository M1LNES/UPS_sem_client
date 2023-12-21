import socket
import threading
import tkinter as tk
import utils.client_to_server_messages as messageHandler
import utils.validation as validate
from tkinter import ttk

class ChatClient:
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

    def connect_to_server(self):
        ip = self.server_ip_entry.get()
        port = int(self.server_port_entry.get())
        nickname = messageHandler.create_message(self.nickname_entry.get())

        if not (validate.validate_name(nickname) and validate.validate_server_ip(ip) and validate.validate_port(port)):
            return

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((ip, port))

            # Start a separate thread to handle server responses
            self.response_thread = threading.Thread(target=self.handle_server_response)
            self.response_thread.start()

            # Send nickname to the server
            self.server.sendall((nickname + "\n").encode())

            # Disable input fields and button after connecting
            # self.server_ip_entry.config(state="disabled")
            # self.server_port_entry.config(state="disabled")
            # self.nickname_entry.config(state="disabled")
            # self.connect_button.config(state="disabled")

            # Open a new window for the chat
            self.open_chat_window(nickname)

            # Close the initial login window
            self.root.withdraw()  # Hide the window instead of destroying it
        except Exception as e:
            print(f"Error connecting: {str(e)}")

    def open_chat_window(self, nickname):
        chat_window = tk.Toplevel()
        chat_window.title(f"Chat Window - {nickname}")

        # Add labels and other widgets to the new window
        ttk.Label(chat_window, text="Welcome to the chat!").pack(pady=10)

        self.message_entry = ttk.Entry(chat_window)
        self.message_entry.pack(pady=5, fill="x", expand=True)

        self.send_button = ttk.Button(chat_window, text="Send", command=self.send_message)
        self.send_button.pack(pady=10)

        # You can add more widgets and labels to the new window as needed.

    def send_message(self):
        message = self.message_entry.get()
        if not message:
            return

        try:
            # Send the message to the server
            self.server.sendall((message + "\n").encode())
            self.message_entry.delete(0, "end")  # Clear the message entry after sending
        except Exception as e:
            print(f"Error sending message: {str(e)}")

    def handle_server_response(self):
        while True:
            try:
                response = self.server.recv(1024).decode()
                if not response:
                    print("Server disconnected.")
                    break
                print("Server reply:", response, end="")
            except Exception as e:
                print(f"Error reading from server: {str(e)}")
                break

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
