import subprocess
import time

HOTSPOT_NAME = "DillyKindle-Hotspot"
HOTSPOT_SSID = "DillyKindle"
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


def start_hotspot():
    nmcli("connection", "down", "homewifi")
    nmcli("connection", "down", TEMP_WIFI_NAME)
    nmcli("radio", "wifi", "on")
    run_command(["sudo", "rfkill", "unblock", "wifi"])

    nmcli("connection", "down", HOTSPOT_NAME)
    nmcli("connection", "delete", HOTSPOT_NAME)

    nmcli("connection", "add", "type", "wifi", "ifname", "wlan0", "con-name", HOTSPOT_NAME, "ssid", HOTSPOT_SSID)
    nmcli("connection", "modify", HOTSPOT_NAME, "802-11-wireless.mode", "ap")
    nmcli("connection", "modify", HOTSPOT_NAME, "802-11-wireless.band", "bg")
    nmcli("connection", "modify", HOTSPOT_NAME, "ipv4.method", "shared")
    nmcli("connection", "modify", HOTSPOT_NAME, "ipv6.method", "ignore")
    nmcli("connection", "modify", HOTSPOT_NAME, "autoconnect", "no")

    return nmcli("connection", "up", HOTSPOT_NAME)

def stop_hotspot():
    return nmcli("connection", "down", HOTSPOT_NAME)


def connect_temporary_wifi(ssid, password):
    stop_hotspot()

    nmcli("connection", "delete", TEMP_WIFI_NAME)

    nmcli("connection", "add", "type", "wifi", "ifname", "wlan0", "con-name", TEMP_WIFI_NAME, "ssid", ssid)
    nmcli("connection", "modify", TEMP_WIFI_NAME, "wifi-sec.key-mgmt", "wpa-psk")
    nmcli("connection", "modify", TEMP_WIFI_NAME, "wifi-sec.psk", password)
    nmcli("connection", "modify", TEMP_WIFI_NAME, "autoconnect", "no")

    return nmcli("connection", "up", TEMP_WIFI_NAME)


def connect_temporary_wifi_after_delay(ssid, password, delay=2):
    time.sleep(delay)
    connect_temporary_wifi(ssid, password)


def wifi_status():
    result = run_command(["nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show", "--active"])
    text = result.stdout

    if f"{TEMP_WIFI_NAME}:wlan0" in text:
        return "connected"

    if "homewifi:wlan0" in text:
        return "connected"

    if f"{HOTSPOT_NAME}:wlan0" in text:
        return "setup"

    return "off"
