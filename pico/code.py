import time
import board
import digitalio
import usb_cdc

COMMAND_PORT = usb_cdc.data

PIN_MAP = {
    "UP": board.GP15,
    "DOWN": board.GP11,
    "SELECT": board.GP7,
    "BACK": board.GP3,
    "POWER": board.GP16,
}

buttons = {}

for name, pin in PIN_MAP.items():
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    buttons[name] = {
        "button": button,
        "was_pressed": False,
        "last_press_time": 0,
    }

select_consumed = False


def send_command(command):
    if COMMAND_PORT is not None:
        COMMAND_PORT.write((command + "\n").encode("utf-8"))


while True:
    now = time.monotonic()

    pressed = {
        name: not item["button"].value
        for name, item in buttons.items()
    }

    for name, item in buttons.items():
        is_pressed = pressed[name]
        was_pressed = item["was_pressed"]

        if is_pressed and not was_pressed and now - item["last_press_time"] > 0.18:
            if name == "UP":
                if pressed["SELECT"]:
                    send_command("ZOOM_IN")
                    select_consumed = True
                else:
                    send_command("UP")

            elif name == "DOWN":
                if pressed["SELECT"]:
                    send_command("ZOOM_OUT")
                    select_consumed = True
                else:
                    send_command("DOWN")

            elif name == "SELECT":
                select_consumed = False

            elif name == "BACK":
                send_command("BACK")

            elif name == "POWER":
                send_command("POWER")

            item["last_press_time"] = now

        if name == "SELECT" and was_pressed and not is_pressed:
            if not select_consumed and now - item["last_press_time"] > 0.05:
                send_command("SELECT")

            select_consumed = False

        item["was_pressed"] = is_pressed

    time.sleep(0.01)
