import time
import board
import digitalio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

keyboard = Keyboard(usb_hid.devices)

button_map = [
    (board.GP15, Keycode.W),
    (board.GP11, Keycode.S),
    (board.GP7, Keycode.E),
    (board.GP3, Keycode.Q),
    (board.GP16, Keycode.X),
]

buttons = []

for pin, key in button_map:
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    buttons.append({
        "button": button,
        "key": key,
        "was_pressed": False,
        "last_press_time": 0,
    })

while True:
    now = time.monotonic()

    for item in buttons:
        is_pressed = not item["button"].value

        if is_pressed and not item["was_pressed"] and now - item["last_press_time"] > 0.18:
            keyboard.press(item["key"])
            time.sleep(0.02)
            keyboard.release(item["key"])
            time.sleep(0.02)
            keyboard.press(Keycode.ENTER)
            time.sleep(0.02)
            keyboard.release(Keycode.ENTER)
            item["last_press_time"] = now

        item["was_pressed"] = is_pressed

    time.sleep(0.01)
