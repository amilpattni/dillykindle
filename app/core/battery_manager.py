import socket
import re


def get_battery_percent():
    try:
        with socket.create_connection(("127.0.0.1", 8423), timeout=0.4) as sock:
            sock.sendall(b"get battery\n")
            data = sock.recv(128).decode("utf-8", errors="ignore")
    except Exception:
        return None

    match = re.search(r"battery:\s*([0-9]+(?:\.[0-9]+)?)", data)

    if match is None:
        return None

    try:
        value = float(match.group(1))
    except Exception:
        return None

    return max(0, min(100, round(value)))


def get_battery_text():
    percent = get_battery_percent()

    if percent is None:
        return "--%"

    return f"{percent}%"
