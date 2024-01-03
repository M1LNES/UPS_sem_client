import re
import tkinter as tk
from tkinter import ttk


def validate_name(name):
    pattern = re.compile(r'^[a-zA-Z0-9_]+$')
    return bool(pattern.match(name))


def validate_port(port):
    port_str = str(port)
    pattern = re.compile(r'^[1-9]\d*$')
    return bool(pattern.match(port_str))


def validate_server_ip(server_ip):
    ip = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    if ip.match(server_ip) or server_ip.lower() == "localhost":
        return True
    else:
        return False


def pop_alert_invalid_login_params(parent):
    info_message = (
        f"Invalid Parameters! \n\n"
        f"Inserted parameters were not right!\n"
        f"Make sure that: \n"
        f"- nickname is using only numbers or english letters \n"
        f"- IP address is 4 numbers divided by dots (192.168.8.10. e.g.)\n"
        f"- port is number"
    )

    alert_window = tk.Toplevel(parent)
    alert_window.title("Error during validating form")

    label = ttk.Label(alert_window, text=info_message)
    label.pack(padx=10, pady=10)


def pop_alert_not_joined(parent):
    info_message = (
        f"Could not join to server! \n\n"
        f"Ensure that server is on-line or that inserted params are valid!\n"
    )

    alert_window = tk.Toplevel(parent)
    alert_window.title("Error during connecting to server")

    label = ttk.Label(alert_window, text=info_message)
    label.pack(padx=10, pady=10)


def pop_alert_connection_lost(parent):
    info_message = (
        f"Lost connection with server! \n\n"
        f"You have 60 seconds to join back - if your connection is not gonna be back in next 25 seconds,\n you will be"
        f"disconnected, but still you have 30 seconds to join back with your name to retrieve state.\n"
    )

    alert_window = tk.Toplevel(parent)
    alert_window.title("Connection lost!")

    label = ttk.Label(alert_window, text=info_message)
    label.pack(padx=10, pady=10)

def pop_alert_disconnected(parent):
    info_message = (
        f"Closing connection! \n\n"
        f"You were unavailable for 30 seconds. You still have 30 seconds to join back. \n"
    )

    alert_window = tk.Toplevel(parent)
    alert_window.title("Closing connection!")

    label = ttk.Label(alert_window, text=info_message)
    label.pack(padx=10, pady=10)

def pop_alert_already_in_game(parent):
    info_message = (
        f"Could not join the lobby! \n\n"
        f"Lobby is in game or full. \n"
    )

    alert_window = tk.Toplevel(parent)
    alert_window.title("Error during joining lobby!")

    label = ttk.Label(alert_window, text=info_message)
    label.pack(padx=10, pady=10)