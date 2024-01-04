import re
import tkinter as tk
from tkinter import ttk


# Manager of validation
# contains a lot of functions that validates message bodies

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
        f"You have 60 seconds to join back - if your connection is not gonna be back in next 25 seconds,\n you will be "
        f"disconnected, but still you have 30 seconds to join back with your name to retrieve state.\n"
    )

    alert_window = tk.Toplevel(parent)
    alert_window.title("Connection lost!")

    label = ttk.Label(alert_window, text=info_message)
    label.pack(padx=10, pady=10)


def pop_alert_disconnected(parent):
    info_message = (
        f"Closing connection! \n\n"
        f"You were disconnect from server.\n"
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


def validate_lobby_info_type(message):
    pattern = re.compile(
        r'^[a-zA-Z0-9]+\|\d+(\.\d+)?\|\d+(\.\d+)?\|[01](;[a-zA-Z0-9]+\|\d+(\.\d+)?\|\d+(\.\d+)?\|[01])*$')

    if not pattern.match(message):
        return False

    segments = message.split(';')

    for segment in segments:
        params = segment.split('|')[1:4]
        param_ints = [int(float(param)) for param in params]
        if param_ints[0] <= 0 or param_ints[1] < 0 or param_ints[0] < param_ints[1]:
            return False

    return True

def validate_lobby_join_response(message):
    return message=="1"

def validate_can_game_start(message):
    pattern = re.compile(r'^[01]\|(\d+)\|(\d+)$')

    if not pattern.match(message):
        return False

    current_players, max_players = map(int, pattern.match(message).groups())
    return 0 <= current_players <= max_players and max_players > 0

def validate_game_started_init(message):
    segments = message.split('|')

    if len(segments) == 4:
        player_info = segments[0].split(';')
        nicknames = []
        points = {}

        try:
            for player_data in player_info:
                player_data_parts = player_data.split(':')
                if len(player_data_parts) == 2:
                    nickname, points_str = player_data_parts
                    nicknames.append(nickname)
                    points[nickname] = int(points_str)
        except ValueError:
            return False

        return True

    return False

def validate_setence_gussed(message):
    try:
        segments = message.split("|")

        if len(segments) == 3:
            player_info = segments[2].split(";")
            nicknames = []
            points = {}

            for player_data in player_info:
                player_data_parts = player_data.split(':')
                if len(player_data_parts) == 2:
                    nickname, points_str = player_data_parts
                    nicknames.append(nickname)
                    points[nickname] = int(points_str)

            return True
    except (ValueError, IndexError):
        pass

    return False

def validate_game_ending(message):
    pattern = re.compile(r'^[a-zA-Z0-9_]+(;[a-zA-Z0-9_]+)*$')
    return bool(pattern.match(message))

def validate_pending_user(message):
    pattern = re.compile(r'^[a-zA-Z0-9_]+$')
    return bool(pattern.match(message))

def validate_connected_user(message):
    pattern = re.compile(r'^[a-zA-Z0-9_]+$')
    return bool(pattern.match(message))

def validate_retrieving_state(message):
    segments = message.split('|')

    if len(segments) == 5:
        player_info = segments[0].split(';')
        nicknames = []
        points = {}

        try:
            for player_data in player_info:
                player_data_parts = player_data.split(':')
                if len(player_data_parts) == 2:
                    nickname, points_str = player_data_parts
                    nicknames.append(nickname)
                    points[nickname] = int(points_str)
        except ValueError:
            return False

        if segments[4] in ('1', '0'):
            return True
        else:
            return False

    return False