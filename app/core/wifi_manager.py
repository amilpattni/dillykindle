import subprocess
import time

HOTSPOT_NAME = "DillyKindle-Hotspot"
HOTSPOT_SSID = "dillykindle"
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


def start_hotspot():
    nmcli("radio", "wifi", "on")

    nmcli("connection", "down", TEMP_WIFI_NAME)
    nmcli("connection", "down", "homewifi")
    nmcli("connection", "down", HOTSPOT_NAME)
    nmcli("connection", "delete", HOTSPOT_NAME)

    nmcli("connection", "add", "type", "wifi", "ifname", "wlan0", "con-name", HOTSPOT_NAME, "ssid", HOTSPOT_SSID)
    nmcli("connection", "modify", HOTSPOT_NAME, "802-11-wireless.mode", "ap")
    nmcli("connection", "modify", HOTSPOT_NAME, "802-11-wireless.band", "bg")
    nmcli("connection", "modify", HOTSPOT_NAME, "ipv4.method", "shared")
    nmcli("connection", "modify", HOTSPOT_NAME, "ipv6.method", "ignore")
    nmcli("connection", "modify", HOTSPOT_NAME, "connection.autoconnect", "no")

    return nmcli("connection", "up", HOTSPOT_NAME)


def stop_hotspot():
    return nmcli("connection", "down", HOTSPOT_NAME)


def hotspot_is_active():
    return get_active_wifi_connection() == HOTSPOT_NAME


def get_upload_url():
    return "http://10.42.0.1:8080"


def connect_temporary_wifi(ssid, password):
    nmcli("radio", "wifi", "on")
    stop_hotspot()

    nmcli("connection", "delete", TEMP_WIFI_NAME)

    nmcli("connection", "add", "type", "wifi", "ifname", "wlan0", "con-name", TEMP_WIFI_NAME, "ssid", ssid)
    nmcli("connection", "modify", TEMP_WIFI_NAME, "wifi-sec.key-mgmt", "wpa-psk")
    nmcli("connection", "modify", TEMP_WIFI_NAME, "wifi-sec.psk", password)
    nmcli("connection", "modify", TEMP_WIFI_NAME, "connection.autoconnect", "no")

    return nmcli("connection", "up", TEMP_WIFI_NAME)


def connect_temporary_wifi_after_delay(ssid, password, delay=2):
    time.sleep(delay)
    return connect_temporary_wifi(ssid, password)


def wifi_status():
    active = get_active_wifi_connection()

    if active == HOTSPOT_NAME:
        return "hotspot"

    if active:
        return "connected"

    return "off"
