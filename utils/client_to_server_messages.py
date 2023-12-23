from constants import message_constants


def create_nick_message(nick):
    len_nick = str(len(nick)).zfill(3)
    formatted_message = f"{message_constants.MAGIC}{len_nick}{message_constants.NICK_TYPE}{nick}"
    return formatted_message


def is_message_valid(message):
    if len(message) < (
            len(message_constants.MAGIC) + message_constants.MESSAGE_TYPE_LENGTH + message_constants.MESSAGE_TYPE_LENGTH):
        return False
    # Magic
    magic = message[:len(message_constants.MAGIC)]
    if magic != message_constants.MAGIC:
        print(f"Magic: {magic}, Constant: {message_constants.MAGIC}")
        return False

    # Message Length
    length_str = message[
                 len(message_constants.MAGIC):len(message_constants.MAGIC) + message_constants.MESSAGE_LENGTH_FORMAT]

    try:
        length = int(length_str)
    except ValueError:
        return False

    # Is message length valid?
    if length != len(message) - len(
            message_constants.MAGIC) - message_constants.MESSAGE_LENGTH_FORMAT - message_constants.MESSAGE_TYPE_LENGTH:
        print(
            f"LengthFromMessage: {length}, CalculatedLength: {len(message) - len(message_constants.MAGIC) - message_constants.MESSAGE_LENGTH_FORMAT - message_constants.MESSAGE_TYPE_LENGTH}")
        return False

    return True


def extract_lobbies_info(message):
    lobby_strings = message.split(';')
    lobbies = []

    for lobby_string in lobby_strings:
        lobby_components = lobby_string.split('|')
        if len(lobby_components) == 4:
            nick, max_players, current_players, game_status = lobby_components

            lobby_info = {
                'nick': nick,
                'max_players': int(max_players),
                'current_players': int(current_players),
                'game_status': int(game_status),
            }

            lobbies.append(lobby_info)

    return lobbies


def create_lobby_joining_message(lobby_name):
    len_name = str(len(lobby_name)).zfill(3)
    formatted_message = f"{message_constants.MAGIC}{len_name}{message_constants.JOIN_TYPE}{lobby_name}"
    print("FORMAT MESAGE: ", formatted_message)
    return formatted_message


def joined_lobby_successfully(message):
    return message == "1"
