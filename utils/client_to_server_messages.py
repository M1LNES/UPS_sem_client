from constants import message_constants


def create_message(nick):
    len_nick = str(len(nick)).zfill(3)
    formatted_message = f"{message_constants.MAGIC}{len_nick}{message_constants.NICK_TYPE}{nick}"
    return formatted_message
