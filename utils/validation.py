import re


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
