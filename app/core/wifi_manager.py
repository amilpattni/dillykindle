import subprocess

TEMP_WIFI_NAME = "DillyKindle-TempWifi"


def run_command(command):
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def nmcli(*args):
    return run_command(["sudo", "nmcli", *args])


def connect_temporary_wifi(ssid, password):
    nmcli("connection", "delete", TEMP_WIFI_NAME)

    nmcli("connection", "add", "type", "wifi", "ifname", "wlan0", "con-name", TEMP_WIFI_NAME, "ssid", ssid)
    nmcli("connection", "modify", TEMP_WIFI_NAME, "wifi-sec.key-mgmt", "wpa-psk")
    nmcli("connection", "modify", TEMP_WIFI_NAME, "wifi-sec.psk", password)
    nmcli("connection", "modify", TEMP_WIFI_NAME, "autoconnect", "no")

    return nmcli("connection", "up", TEMP_WIFI_NAME)


def wifi_status():
    result = run_command(["nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show", "--active"])
    text = result.stdout

    if ":wlan0" in text:
        return "connected"

    return "off"
