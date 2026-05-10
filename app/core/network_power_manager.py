import subprocess


def run_command(command):
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def nmcli(*args):
    return run_command(["sudo", "nmcli", *args])


def get_active_wifi_connection():
    result = run_command(["nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show", "--active"])

    for line in result.stdout.splitlines():
        parts = line.split(":")
        if len(parts) >= 2 and parts[-1] == "wlan0":
            return parts[0]

    return None


def wifi_off():
    return nmcli("radio", "wifi", "off")


def wifi_on():
    return nmcli("radio", "wifi", "on")


def wifi_is_connected():
    return get_active_wifi_connection() is not None
